import Foundation
import Security

// MARK: - Sovereign Identity (Secure Enclave)

class SovereignIdentity {
    let tag = "com.sovereigncore.identity.v4".data(using: .utf8)!
    
    func getPrivateKey() -> SecKey? {
        let query: [String: Any] = [
            kSecClass as String: kSecClassKey,
            kSecAttrKeyType as String: kSecAttrKeyTypeECSECPrimeRandom,
            kSecAttrApplicationTag as String: tag,
            kSecAttrTokenID as String: kSecAttrTokenIDSecureEnclave,
            kSecReturnRef as String: true
        ]
        
        var item: CFTypeRef?
        let status = SecItemCopyMatching(query as CFDictionary, &item)
        
        if status == errSecSuccess {
            return (item as! SecKey)
        }
        
        return generateKey()
    }
    
    private func generateKey() -> SecKey? {
        guard let access = SecAccessControlCreateWithFlags(
            kCFAllocatorDefault,
            kSecAttrAccessibleWhenUnlockedThisDeviceOnly,
            .privateKeyUsage,
            nil
        ) else { return nil }
        
        let attributes: [String: Any] = [
            kSecAttrKeyType as String: kSecAttrKeyTypeECSECPrimeRandom,
            kSecAttrKeySizeInBits as String: 256,
            kSecAttrTokenID as String: kSecAttrTokenIDSecureEnclave,
            kSecPrivateKeyAttrs as String: [
                kSecAttrIsPermanent as String: true,
                kSecAttrApplicationTag as String: tag,
                kSecAttrAccessControl as String: access
            ]
        ]
        
        var error: Unmanaged<CFError>?
        guard let key = SecKeyCreateRandomKey(attributes as CFDictionary, &error) else {
            fputs("SEP Key Generation Error: \(error!.takeRetainedValue().localizedDescription)\n", stderr)
            return nil
        }
        return key
    }
    
    func getPublicKey() -> SecKey? {
        guard let privateKey = getPrivateKey() else { return nil }
        return SecKeyCopyPublicKey(privateKey)
    }
    
    func sign(data: Data) -> Data? {
        guard let key = getPrivateKey() else { return nil }
        var error: Unmanaged<CFError>?
        
        let signature = SecKeyCreateSignature(
            key,
            .ecdsaSignatureMessageX962SHA256,
            data as CFData,
            &error
        )
        return signature as Data?
    }
    
    func getPublicKeyHex() -> String? {
        guard let publicKey = getPublicKey(),
              let data = SecKeyCopyExternalRepresentation(publicKey, nil) as Data? else {
            return nil
        }
        return data.map { String(format: "%02x", $0) }.joined()
    }
}

// MARK: - Thermal Telemetry

struct ThermalTelemetry {
    static func getState() -> String {
        let state = ProcessInfo.processInfo.thermalState
        switch state {
        case .nominal: return "NOMINAL"
        case .fair: return "FAIR"
        case .serious: return "SERIOUS"
        case .critical: return "CRITICAL"
        @unknown default: return "UNKNOWN"
        }
    }
    
    static func getProcessUsage() -> [String: Any] {
        var hostStats = host_cpu_load_info()
        let HOST_CPU_LOAD_INFO_COUNT = mach_msg_type_number_t(MemoryLayout<host_cpu_load_info_data_t>.size / MemoryLayout<integer_t>.size)
        var count = HOST_CPU_LOAD_INFO_COUNT
        let result = withUnsafeMutablePointer(to: &hostStats) {
            $0.withMemoryRebound(to: integer_t.self, capacity: Int(count)) {
                host_statistics(mach_host_self(), HOST_CPU_LOAD_INFO, $0, &count)
            }
        }
        
        var loadDict: [String: Any] = [:]
        if result == KERN_SUCCESS {
            loadDict["user"] = hostStats.cpu_ticks.0
            loadDict["system"] = hostStats.cpu_ticks.1
            loadDict["idle"] = hostStats.cpu_ticks.2
            loadDict["nice"] = hostStats.cpu_ticks.3
        }
        return loadDict
    }
    
    static func getMemoryUsage() -> [String: Any] {
        var stats = vm_statistics64()
        var count = mach_msg_type_number_t(MemoryLayout<vm_statistics64_data_t>.size / MemoryLayout<integer_t>.size)
        let result = withUnsafeMutablePointer(to: &stats) {
            $0.withMemoryRebound(to: integer_t.self, capacity: Int(count)) {
                host_statistics64(mach_host_self(), HOST_VM_INFO64, $0, &count)
            }
        }
        
        let pageSize = UInt64(vm_kernel_page_size)
        if result == KERN_SUCCESS {
            return [
                "free": UInt64(stats.free_count) * pageSize,
                "active": UInt64(stats.active_count) * pageSize,
                "inactive": UInt64(stats.inactive_count) * pageSize,
                "wire": UInt64(stats.wire_count) * pageSize,
                "compressed": UInt64(stats.compressor_page_count) * pageSize
            ]
        }
        return [:]
    }
    
    static func getSystemLoad() -> [String: Any] {
        let processInfo = ProcessInfo.processInfo
        return [
            "thermal_state": getState(),
            "processor_count": processInfo.processorCount,
            "active_processor_count": processInfo.activeProcessorCount,
            "physical_memory_gb": Double(processInfo.physicalMemory) / 1_073_741_824,
            "system_uptime": processInfo.systemUptime,
            "is_low_power_mode": processInfo.isLowPowerModeEnabled,
            "cpu_usage": getProcessUsage(),
            "memory_usage": getMemoryUsage()
        ]
    }
}

// MARK: - CLI Interface

func printJSON(_ dict: [String: Any]) {
    if let data = try? JSONSerialization.data(withJSONObject: dict, options: .prettyPrinted),
       let string = String(data: data, encoding: .utf8) {
        print(string)
    }
}

func main() {
    let args = CommandLine.arguments
    let identity = SovereignIdentity()
    
    guard args.count > 1 else {
        printJSON([
            "error": "No command specified",
            "commands": ["thermal", "identity", "sign", "verify", "status"]
        ])
        exit(1)
    }
    
    switch args[1] {
    case "thermal":
        let telemetry = ThermalTelemetry.getSystemLoad()
        printJSON(telemetry)
        
    case "identity":
        if let pubKeyHex = identity.getPublicKeyHex() {
            printJSON([
                "status": "verified",
                "public_key": pubKeyHex,
                "algorithm": "ECDSA-P256",
                "enclave": "SEP"
            ])
        } else {
            printJSON([
                "status": "unavailable",
                "reason": "SEP key generation requires device unlock"
            ])
        }
        
    case "sign":
        guard args.count > 2 else {
            printJSON(["error": "No data to sign"])
            exit(1)
        }
        let dataToSign = args[2].data(using: .utf8)!
        if let signature = identity.sign(data: dataToSign) {
            printJSON([
                "status": "signed",
                "signature": signature.base64EncodedString(),
                "input_hash": dataToSign.base64EncodedString()
            ])
        } else {
            printJSON(["status": "failed", "reason": "SEP signing unavailable"])
        }
        
    case "status":
        let thermal = ThermalTelemetry.getSystemLoad()
        var status: [String: Any] = [
            "version": "SovereignCore v4.0",
            "thermal": thermal,
            "timestamp": ISO8601DateFormatter().string(from: Date())
        ]
        if let pubKey = identity.getPublicKeyHex() {
            status["identity"] = ["status": "verified", "public_key_prefix": String(pubKey.prefix(32)) + "..."]
        } else {
            status["identity"] = ["status": "software_fallback"]
        }
        printJSON(status)
        
    default:
        printJSON(["error": "Unknown command: \(args[1])"])
        exit(1)
    }
}

main()
