import Foundation
import Security
import IOKit

// MARK: - Sovereign Identity (Secure Enclave Integration)

class SovereignIdentity {
    let tag = "com.sovereigncore.identity.v4".data(using: .utf8)!
    
    // Generate or Retrieve Key from Secure Enclave
    func getPrivateKey() -> SecKey? {
        let query: [String: Any] = [
            kSecClass as String: kSecClassKey,
            kSecAttrApplicationTag as String: tag,
            kSecAttrKeyType as String: kSecAttrKeyTypeECSECPrimeRandom,
            kSecReturnRef as String: true
        ]
        
        var item: CFTypeRef?
        let status = SecItemCopyMatching(query as CFDictionary, &item)
        
        if status == errSecSuccess {
            return (item as! SecKey)
        }
        
        // If not found, create new in Secure Enclave
        return generateKey()
    }
    
    private func generateKey() -> SecKey? {
        // Access Control: Device must be unlocked
        var error: Unmanaged<CFError>?
        guard let access = SecAccessControlCreateWithFlags(
            kCFAllocatorDefault,
            kSecAttrAccessibleWhenUnlockedThisDeviceOnly,
            .privateKeyUsage,
            &error
        ) else {
            print("❌ ACCESS_CONTROL_FAILED")
            if let err = error?.takeRetainedValue() {
                print("Error: \(err.localizedDescription)")
            }
            return nil
        }
        
        // Key attributes - FORCE Secure Enclave usage
        let attributes: [String: Any] = [
            kSecAttrKeyType as String: kSecAttrKeyTypeECSECPrimeRandom,
            kSecAttrKeySizeInBits as String: 256,
            kSecAttrTokenID as String: kSecAttrTokenIDSecureEnclave,  // CRITICAL: Forces SEP
            kSecAttrApplicationTag as String: tag,
            kSecPrivateKeyAttrs as String: [
                kSecAttrIsPermanent as String: true,
                kSecAttrAccessControl as String: access
            ]
        ]
        
        error = nil
        guard let key = SecKeyCreateRandomKey(attributes as CFDictionary, &error) else {
            if let err = error?.takeRetainedValue() {
                print("❌ KEY_GENERATION_FAILED: \(err.localizedDescription)")
            }
            return nil
        }
        
        print("✅ KEY_GENERATED_IN_SEP")
        return key
    }
    
    func sign(data: String) -> String? {
        guard let key = getPrivateKey() else {
            print("❌ KEY_NOT_FOUND")
            return nil
        }
        
        let dataToSign = data.data(using: .utf8)!
        
        var error: Unmanaged<CFError>?
        guard let signature = SecKeyCreateSignature(
            key,
            .ecdsaSignatureMessageX962SHA256,
            dataToSign as CFData,
            &error
        ) else {
            print("❌ SIGNING_FAILED")
            if let err = error?.takeRetainedValue() {
                print("Error: \(err.localizedDescription)")
            }
            return nil
        }
        
        return (signature as Data).base64EncodedString()
    }
    
    func verify(data: String, signature: String) -> Bool {
        guard let privateKey = getPrivateKey() else {
            print("❌ KEY_NOT_FOUND")
            return false
        }
        
        guard let publicKey = SecKeyCopyPublicKey(privateKey) else {
            print("❌ PUBLIC_KEY_FAILED")
            return false
        }
        
        let dataToVerify = data.data(using: .utf8)!
        guard let signatureData = Data(base64Encoded: signature) else {
            print("❌ INVALID_SIGNATURE_FORMAT")
            return false
        }
        
        var error: Unmanaged<CFError>?
        let isValid = SecKeyVerifySignature(
            publicKey,
            .ecdsaSignatureMessageX962SHA256,
            dataToVerify as CFData,
            signatureData as CFData,
            &error
        )
        
        return isValid
    }
}

// MARK: - Thermal Telemetry (SMC Integration)

class ThermalMonitor {
    
    func getThermalState() -> [String: Any] {
        let state = ProcessInfo.processInfo.thermalState
        var stateString = "UNKNOWN"
        
        switch state {
        case .nominal:
            stateString = "NOMINAL"
        case .fair:
            stateString = "FAIR"
        case .serious:
            stateString = "SERIOUS"
        case .critical:
            stateString = "CRITICAL"
        @unknown default:
            stateString = "UNKNOWN"
        }
        
        // Get CPU temperature (simplified - full SMC implementation would read Tp09, Tp0t keys)
        let cpuTemp = getCPUTemperature()
        
        return [
            "state": stateString,
            "cpu_temp": cpuTemp,
            "timestamp": Date().timeIntervalSince1970,
            "thermal_pressure": getThermalPressure()
        ]
    }
    
    private func getCPUTemperature() -> Double {
        // Simplified implementation using ProcessInfo
        // Full implementation would use IOKit to read SMC keys (Tp09, Tp0t for Apple Silicon)
        // This requires IOConnectCallStructMethod which is complex
        
        // For now, estimate based on thermal state
        let state = ProcessInfo.processInfo.thermalState
        switch state {
        case .nominal:
            return 45.0
        case .fair:
            return 65.0
        case .serious:
            return 80.0
        case .critical:
            return 95.0
        @unknown default:
            return 40.0
        }
    }
    
    private func getThermalPressure() -> Double {
        // Thermal pressure as a 0.0-1.0 value
        let state = ProcessInfo.processInfo.thermalState
        switch state {
        case .nominal:
            return 0.0
        case .fair:
            return 0.3
        case .serious:
            return 0.7
        case .critical:
            return 1.0
        @unknown default:
            return 0.0
        }
    }
}

// MARK: - Main Entry Point

let args = CommandLine.arguments
let identity = SovereignIdentity()
let thermal = ThermalMonitor()

func printJSON(_ data: [String: Any]) {
    if let jsonData = try? JSONSerialization.data(withJSONObject: data, options: []),
       let jsonString = String(data: jsonData, encoding: .utf8) {
        print(jsonString)
    } else {
        print("{\"error\": \"JSON serialization failed\"}")
    }
}

if args.count < 2 {
    print("Usage: sovereign_bridge [keygen|sign <data>|verify <data> <signature>|telemetry]")
    exit(1)
}

let command = args[1]

switch command {
case "keygen":
    if identity.getPrivateKey() != nil {
        printJSON(["status": "success", "message": "Key generated or retrieved from SEP"])
    } else {
        printJSON(["status": "error", "message": "Key generation failed"])
        exit(1)
    }
    
case "sign":
    guard args.count >= 3 else {
        printJSON(["status": "error", "message": "Missing data to sign"])
        exit(1)
    }
    
    if let signature = identity.sign(data: args[2]) {
        printJSON(["status": "success", "signature": signature])
    } else {
        printJSON(["status": "error", "message": "Signing failed"])
        exit(1)
    }
    
case "verify":
    guard args.count >= 4 else {
        printJSON(["status": "error", "message": "Missing data or signature"])
        exit(1)
    }
    
    let isValid = identity.verify(data: args[2], signature: args[3])
    printJSON(["status": "success", "valid": isValid])
    
case "telemetry":
    let data = thermal.getThermalState()
    printJSON(data)
    
default:
    printJSON(["status": "error", "message": "Unknown command: \(command)"])
    exit(1)
}
