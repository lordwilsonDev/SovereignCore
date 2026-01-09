# Systems Integration Report: Heterogeneous Distributed Inference Architecture via IP over Thunderbolt (Windows 11 & macOS)

## 1. Executive Summary

The escalating computational demands of Large Language Models (LLMs) have precipitated a resource scarcity crisis in consumer and prosumer hardware environments. State-of-the-art foundation models, such as Llama-3-70B, DeepSeek-V3, and Qwen-2.5-72B, necessitate Video Random Access Memory (VRAM) capacities that frequently exceed the 24GB ceiling of flagship consumer Graphics Processing Units (GPUs) like the NVIDIA RTX 4090.

This report presents an exhaustive architectural analysis and implementation guide for a heterogeneous distributed inference system. This system leverages the complementary strengths of two distinct hardware ecosystems: the high-throughput CUDA acceleration of Windows 11 workstations and the massive Unified Memory Architecture (UMA) of Apple Silicon (macOS) devices. The unifying interconnect for this architecture is IP over Thunderbolt (IPoTB), a protocol capable of bridging the latency and bandwidth gaps that typically render network-distributed inference unviable for local deployments.

The technical challenge of this integration is non-trivial. It requires overcoming significant interoperability barriers between the Windows 11 USB4 networking stack and the macOS Thunderbolt Bridge service. Furthermore, effective utilization of this link requires precise tuning of the llama.cpp Remote Procedure Call (RPC) framework, specifically regarding tensor splitting strategies (--tensor-split) and parallelism modes (Pipeline vs. Tensor) to preventing the interconnect from becoming a paralyzing bottleneck.

This document serves as a definitive technical manual for systems architects and AI researchers. It details the physical layer prerequisites, operating system network stack engineering, software compilation workflows, and algorithmic optimization strategies required to deploy a stable, high-performance distributed inference cluster using commodity Thunderbolt hardware.

## 2. The Theoretical Framework of Heterogeneous Distributed Inference

To successfully engineer a distributed inference system across a Thunderbolt link, one must first deconstruct the theoretical bottlenecks inherent in distributed computing and how they manifest within the specific topology of a Windows-Mac interconnect. The fundamental tension exists between Compute Latency (the time to process a token) and Communication Latency (the time to move data between nodes).

### 2.1 The Memory Wall and the Bandwidth Hierarchy

In a monolithic local inference setup, the primary bottleneck is the "Memory Wall"—the bandwidth limitation in reading model weights from VRAM to the Compute Unified Device Architecture (CUDA) cores or Apple Neural Engine (ANE).

- **Local Bandwidth**: An NVIDIA RTX 4090 offers approximately 1,008 GB/s of memory bandwidth. An Apple M2 Ultra offers up to 800 GB/s.
- **Interconnect Bandwidth (Thunderbolt 4)**: The theoretical maximum throughput of Thunderbolt 4 is 40 Gbps. However, this bandwidth is shared between video, PCIe tunneling, and data protocols. For peer-to-peer IP networking, the effective throughput is typically encapsulated, resulting in a practical maximum of 15-20 Gbps.
- **The Discrepancy**: This creates a bandwidth hierarchy where the local memory is roughly 400 times faster than the interconnect.

This massive discrepancy dictates that the architecture must be designed to minimize data transfer. A naive distribution strategy, such as one that requires synchronization of full tensor states at high frequency, will fail catastrophically. The system must be optimized to treat the Thunderbolt link as a "narrow pipe" through which only essential activation data flows.

### 2.2 Parallelism Taxonomies in llama.cpp

The llama.cpp library facilitates distributed inference via its RPC backend. Understanding the two primary modes of model parallelism is critical for selecting the correct configuration for a Thunderbolt-constrained environment.

#### 2.2.1 Tensor Parallelism (Row/Column Splitting)

Tensor Parallelism (TP) involves splitting the individual weight matrices (Linear Layers) across multiple devices. For a matrix multiplication $Y = XW$, the weight matrix $W$ is split into $W_1$ and $W_2$. Device A computes $Y_1 = XW_1$ and Device B computes $Y_2 = XW_2$.

- **Synchronization Requirement**: The results $Y_1$ and $Y_2$ must be summed (All-Reduce) to produce the final output $Y$. This synchronization must occur for every single layer in the model, for every token generated.
- **Bandwidth Sensitivity**: This method requires extremely low latency and high bandwidth, typically provided by NVLink (900 GB/s) or PCIe 4.0 x16 (64 GB/s).
- **Thunderbolt Viability**: Near Zero. On a 20 Gbps Thunderbolt link, the latency penalty of synchronizing 80+ layers per token results in inference speeds dropping to < 0.5 tokens per second (t/s).

#### 2.2.2 Pipeline Parallelism (Layer Splitting)

Pipeline Parallelism (PP) involves slicing the model horizontally. Layers 1 through $N$ reside on Node A, while Layers $N+1$ through $M$ reside on Node B.

- **Data Flow**: The input token enters Node A, flows through layers 1-$N$, and the resulting activation tensor is transmitted once across the interconnect to Node B, which processes layers $N+1$ to $M$.
- **Synchronization Requirement**: Communication occurs only at the boundary of the split. For a 2-node split, there is only one transmission per forward pass (token generation).
- **Thunderbolt Viability**: High. The volume of data transferred is limited to the size of the activation tensor (typically a few kilobytes to megabytes depending on batch size), which fits comfortably within the 15-20 Gbps envelope of IP over Thunderbolt.

Consequently, the optimization objective for this report is to enforce a Pipeline Parallel configuration where the Windows PC and Mac operate as distinct stages in a sequential processing line.

## 3. The Physical Layer: Thunderbolt Networking Interoperability

Establishing a stable, low-latency IP connection between Windows 11 and macOS over Thunderbolt is the single most significant implementation hurdle. While the hardware interface (USB-C) is standardized, the software protocols for "IP over Thunderbolt" have diverged significantly between the two operating systems.

### 3.1 Hardware Prerequisites and Cabling Standards

The integrity of the physical layer is non-negotiable. Thunderbolt 4 signals operate at 40 Gbps and are highly susceptible to attenuation and interference.

**Cabling Constraints**:

- **Passive Cables**: Must be under 0.8 meters (approx. 2.6 feet) to support full 40 Gbps throughput.
- **Active Cables**: Required for lengths up to 2.0 meters (approx. 6.5 feet). Active cables contain retimer chips to boost signal integrity.
- **The "USB-C" Trap**: Using a standard USB-C charging cable (USB 2.0 or 3.0) will result in a connection that either fails to negotiate a network link or falls back to 480 Mbps (USB 2.0 speeds), rendering RPC unusable.

**Controller Architecture**:

- **macOS**: All Apple Silicon (M1, M2, M3 families) devices feature integrated Thunderbolt/USB4 controllers that natively support the bridge networking profile.
- **Windows**: Requires a dedicated Thunderbolt 3 or 4 controller (e.g., Intel Maple Ridge JHL8540). Note that while many AMD motherboards support "USB4," they may lack the specific Intel certification for "Thunderbolt Networking," potentially appearing as generic USB devices rather than network adapters.

### 3.2 The Windows 11 Driver Ecosystem Crisis

Windows 11 introduced a paradigm shift in how high-speed USB-C connections are managed, moving away from the legacy "Thunderbolt Networking" driver stack toward the USB4 standard. This transition has created a compatibility chasm.

- **Legacy Mode (Thunderbolt 3)**: Relied on the "Thunderbolt Control Center" application and a specific Intel network driver. This protocol is what macOS expects for its "Thunderbolt Bridge."
- **Modern Mode (USB4)**: Windows 11 natively manages USB4 links. However, without specific legacy drivers, a Windows 11 USB4 host may not advertise itself as a network peer to a Mac, resulting in the connection appearing physically active but logically disconnected (no network adapter appears).

Table 1: Thunderbolt vs. USB4 Networking Compatibility Matrix

| Feature | Legacy Thunderbolt 3 (Win 10/11) | USB4 Native (Win 11) | macOS Thunderbolt Bridge |
| :--- | :--- | :--- | :--- |
| Protocol | Intel Proprietary Networking | USB4NET / CDC-NCM | IP over Thunderbolt (Intel-like) |
| Discovery | Thunderbolt Control Center | Windows Settings | System Settings > Network |
| Default IP | APIPA (169.254.x.x) | APIPA (169.254.x.x) | APIPA (169.254.x.x) |
| Driver | Intel Thunderbolt Networking | Microsoft USB4 | Native XNU Kernel Driver |
| Interop | High Compatibility with Mac | Low/Mixed Compatibility | Native |

### 3.3 Remediation: Forcing Legacy Driver Support

For users encountering the "Missing Network Adapter" issue on Windows 11, it is often necessary to manually install the legacy Intel Thunderbolt Networking drivers, bypassing the default Microsoft USB4 implementation.

**Implementation Procedure**:

1. **Driver Acquisition**: Locate the "Intel Thunderbolt Networking" driver. This is frequently bundled with Intel NUC driver packs or legacy HP/Dell support pages (e.g., SoftPaq sp142981 or similar).
2. **Installation Sequence**:
    - Disconnect the Thunderbolt cable.
    - Uninstall any existing "Thunderbolt" software from Apps & Features.
    - Open Device Manager and remove any "USB4 Router" or "Thunderbolt Controller" devices, checking "Attempt to remove the driver for this device."
    - Install the legacy Intel driver package.
    - Reboot the Windows workstation.
    - Reconnect the Thunderbolt cable.
3. **Verification**: A successful installation will manifest in Device Manager > Network adapters as "Thunderbolt(TM) Networking" or "Intel(R) Ethernet Connection" (virtualized).

## 4. Engineering the Windows 11 Network Stack

Once the physical link allows the operating system to enumerate a network adapter, the logical configuration must be engineered to support high-throughput, low-latency RPC traffic. Windows 11 defaults are optimized for security and standard Ethernet, often impeding high-performance peer-to-peer connections.

### 4.1 Static IP Assignment and Subnetting

By default, both Windows and macOS will resort to Automatic Private IP Addressing (APIPA), assigning addresses in the 169.254.x.x range. While functional for basic discovery, APIPA is non-deterministic. For a robust RPC configuration where command-line arguments require fixed IP targets, a static addressing scheme is mandatory.

**PowerShell Configuration Strategy**:

```powershell
# Step 1: Identify the Interface Index (ifIndex)
# Look for descriptions like "Thunderbolt", "Intel(R) Ethernet", or "Unidentified Network"
Get-NetAdapter | Format-Table Name, InterfaceDescription, ifIndex, Status, MacAddress

# Step 2: Assign Static IP (Assume ifIndex is 12 for this example)
# We use a /24 subnet in the 10.0.x.x range to distinguish from standard 192.168.x.x LANs
New-NetIPAddress -InterfaceIndex 12 -IPAddress 10.0.10.1 -PrefixLength 24 -DefaultGateway $null

# Note: The 'DefaultGateway' must be $null. Defining a gateway on this link
# will cause Windows to attempt to route internet traffic through the Mac,
# leading to connectivity loss.
```

### 4.2 Firewall Traversal and Network Profiles

A common failure mode involves the Thunderbolt link being classified as an "Unidentified Network." Windows security policy defaults unidentified networks to the Public profile, which enforces strict firewall rules, blocking incoming traffic on non-standard ports like 50052 (the default llama.cpp RPC port).

**Remediation via PowerShell**:

```powershell
# Step 1: Force Network Category to Private
# Replace 'Ethernet 4' with the actual name of your Thunderbolt adapter
$tbAdapter = Get-NetConnectionProfile -InterfaceAlias "Ethernet 4"
Set-NetConnectionProfile -InterfaceIndex $tbAdapter.InterfaceIndex -NetworkCategory Private

# Step 2: Create Firewall Rule for RPC Server
# This ensures that even if the profile reverts, the specific binary is whitelisted
New-NetFirewallRule -DisplayName "Llama.cpp RPC Server" `
                    -Direction Inbound `
                    -Program "C:\Users\Admin\llama.cpp\build\bin\Release\rpc-server.exe" `
                    -Action Allow `
                    -Profile Private,Domain,Public `
                    -Protocol TCP `
                    -LocalPort 50052
```

### 4.3 Maximum Transmission Unit (MTU) Tuning

The Maximum Transmission Unit (MTU) defines the largest data packet that can be transmitted without fragmentation. Thunderbolt networking emulates Ethernet, but the virtualization layer supports "Jumbo Frames" to reduce CPU overhead.

- **The Conflict**: macOS often negotiates a Thunderbolt Bridge MTU of 9000 bytes (Jumbo Frames). However, many Windows Thunderbolt drivers are hard-coded to 1500 bytes (Standard Ethernet) or 4088 bytes.
- **The Consequence**: If the Mac sends 9000-byte packets to a Windows host expecting 1500 bytes, the packets must be fragmented or dropped. This process consumes excessive CPU cycles and causes severe latency spikes, often resulting in RPC timeouts during tensor transfer.

**Optimization Procedure**:
It is critical to synchronize the MTU settings. If Windows refuses to accept 9000, macOS must be lowered to 1500.

```powershell
# Check current MTU settings
netsh interface ipv4 show subinterfaces

# Attempt to set Jumbo Frames on Windows
# Note: This command often fails if the underlying NDIS driver does not support it
netsh interface ipv4 set subinterface "Ethernet 4" mtu=9000 store=persistent

# If the above fails or reverts to 1500, accept 1500 as the baseline.
```

## 5. Engineering the macOS Network Stack

The macOS configuration is generally more streamlined due to native kernel support, but it requires precise alignment with the Windows configuration to ensure routing priority.

### 5.1 Configuring the Thunderbolt Bridge Service

1. **Service Creation**: Navigate to System Settings > Network. If "Thunderbolt Bridge" is not listed, use the (...) > Add Service menu to instantiate it.
2. **IP Configuration**:
    - Click Details > TCP/IP.
    - Configure IPv4: Manually.
    - IP Address: 10.0.10.2 (Must be in the same subnet as the Windows host).
    - Subnet Mask: 255.255.255.0.
    - Router: Leave Empty.
3. **Hardware / MTU Configuration**:
    - Click Hardware.
    - Configure: Manually.
    - MTU: This must match the Windows setting exactly. If Windows is locked to 1500, set this to 1500. Do not leave it at "Standard (1500)" or "Jumbo (9000)" without verifying the Windows side; manually typing the value is safer.

### 5.2 Service Order and Routing Priority

macOS prioritizes network interfaces based on the Service Order. If the Thunderbolt Bridge is lower in the list than WiFi, the OS might attempt to route traffic intended for the local subnet via the default gateway (WiFi) if the routing table is ambiguous.

- **Best Practice**: In Network > (...) > Set Service Order, drag Thunderbolt Bridge above Wi-Fi. This ensures that if a route exists on Thunderbolt, it is chosen first.

## 6. Network Validation and Performance Telemetry

Before deploying the llama.cpp application stack, the integrity of the network link must be rigorously validated. A connection that allows simple ICMP "ping" traffic may still exhibit packet loss or jitter under the heavy load of tensor transmission.

### 6.1 Latency and Jitter Analysis

Latency is the primary determinant of token generation speed in distributed inference.

- **Tool**: Terminal (macOS) / PowerShell (Windows).
- **Command**: `ping 10.0.10.1` (from Mac).
- **Benchmark**:
  - Excellent: < 0.8 ms
  - Acceptable: 1.0 - 1.5 ms
  - Problematic: > 2.0 ms (Indicates driver overhead or cable issues).

### 6.2 Throughput Saturation Testing

To verify bandwidth, use `iperf3`. This tool generates synthetic traffic to saturate the link.

- **Windows (Server Mode)**:
  `iperf3 -s`
- **Mac (Client Mode)**:

  ```bash
  # -P 4 runs 4 parallel streams to saturate the bus
  iperf3 -c 10.0.10.1 -P 4
  ```

- **Interpreting the Data**:
  - Target Throughput: 12 Gbps - 20 Gbps.
  - Asymmetry: It is common for Windows-to-Mac throughput to differ from Mac-to-Windows.
  - Troubleshooting: If throughput is capped at ~5 Gbps or ~480 Mbps, the system has likely fallen back to USB 3.0 or 2.0 protocols due to poor cable quality or connector seating.

### 6.3 Automated Reliability Monitoring

Thunderbolt connections can be fragile, often dropping when the host enters sleep states. Implementing a monitoring script is recommended to detect silent failures.

**PowerShell Connectivity Monitor Script**:

```powershell
# Save as Monitor-TB.ps1
$TargetIP = "10.0.10.2"
Write-Host "Monitoring Thunderbolt Link to $TargetIP..." -ForegroundColor Cyan

while ($true) {
    $test = Test-Connection -TargetName $TargetIP -Count 1 -ErrorAction SilentlyContinue
    if ($test.Status -eq "Success") {
        if ($test.ResponseTime -gt 2) {
             Write-Host "High Latency: $($test.ResponseTime) ms" -ForegroundColor Yellow
        } else {
             Write-Host "Link Active: $($test.ResponseTime) ms" -ForegroundColor Green
        }
    } else {
        Write-Host "LINK DOWN - $(Get-Date)" -ForegroundColor Red
        # Optional: Trigger adapter reset
        # Restart-NetAdapter -Name "Ethernet 4"
    }
    Start-Sleep -Seconds 1
}
```

## 7. The llama.cpp RPC Software Architecture

With the network layer stabilized, we proceed to the application layer. The llama.cpp library supports distributed inference via the GGML_RPC backend. This is not a default feature and requires compilation from source with specific flags.

### 7.1 Compilation on Windows (The RPC Server)

The Windows machine acts as the worker node. It must run the `rpc-server` binary to accept tensor computation requests.

- **Prerequisites**: Visual Studio 2022 Community (C++ workload), CMake, CUDA Toolkit, Git.
- **Build Workflow**:

  ```powershell
  git clone https://github.com/ggml-org/llama.cpp
  cd llama.cpp
  mkdir build-rpc
  cd build-rpc
  cmake .. -DGGML_CUDA=ON -DGGML_RPC=ON
  cmake --build . --config Release
  ```

- **Verification**: Check for `rpc-server.exe` in `build-rpc\bin\Release\`.

### 7.2 Compilation on macOS (The Main Host)

The Mac acts as the orchestrator.

- **Build Workflow**:

  ```bash
  cd llama.cpp
  mkdir build-rpc
  cd build-rpc
  cmake .. -DGGML_RPC=ON
  make -j$(sysctl -n hw.ncpu)
  ```

## 8. Algorithmic Optimization of Distributed Inference

The crux of this report lies in optimizing the llama.cpp runtime parameters to balance the load without saturating the bus.

### 8.1 The RPC Server Launch (Windows)

```dos
cd build-rpc\bin\Release
set CUDA_VISIBLE_DEVICES=0
rpc-server.exe -H 10.0.10.1 -p 50052
```

### 8.2 The Split Strategy: Pipeline vs. Row

**CRITICAL**: Use `--split-mode layer` (Pipeline Parallelism).

- **Row Splitting**: Requires sync at every layer. Thunderbolt Latency Kill (~5000 syncs/sec). Result: < 0.1 t/s.
- **Layer Splitting**: Syncs once per forward pass. Throughput matched to Thunderbolt bandwidth. Result: Usable.

### 8.3 Optimizing --tensor-split

- **Heuristic**: Assign layers proportional to memory/compute.
- **Scenario**: Llama-3-70B (40GB). Windows (24GB VRAM) vs Mac (64GB RAM).
- **Target**: Fill Windows GPU to ~85% (leaving room for KV cache).
- **Command**:

  ```bash
  ./llama-cli \
    -m /models/Llama-3-70B-Q4_K_M.gguf \
    --rpc 10.0.10.1:50052 \
    --tensor-split 9,11 \
    -n 1024 \
    -p "System analysis:"
  ```

### 8.4 Context Cache (KV Cache) Management

Always "under-fill" the remote GPU. If VRAM hits 100%, inference crashes. Leave 1-2GB buffer.

## 9. Operational Resilience

- **Sleep/Wake**: Disable PCIe Link State Power Management on Windows.
- **Connection Refused**: Check Windows Firewall (Port 50052) and IP binding.
- **Slow Speed**: Verify cable is not falling back to USB 2.0. Verify `--split-mode layer`.

## 10. Future Horizons: BitNet b1.58

Emerging 1.58-bit models will inevitably solve the bandwidth bottleneck by reducing model size by 3x, making Thunderbolt connections functionally equivalent to PCIe for massive models.

## 11. Conclusion

The integration of Windows 11 and macOS via IP over Thunderbolt creates a potent, albeit complex, distributed inference cluster. By combining the raw compute power of CUDA-enabled GPUs with the massive memory address space of Apple Silicon, users can circumvent VRAM limitations. Success demands a systems engineering approach, but the result is a cost-effective, high-performance inference engine.
