# 🎯 SOVEREIGN AGENT TEST MATRIX
## Goal: Background Agent → Chat Monitor → CLI Agent Pipeline

**Target Architecture:**
```
┌─────────────────────────────────────────────────────────────────┐
│                    SOVEREIGN BACKGROUND AGENT                    │
│  (Persistent Process - Observes, Thinks, Commands)              │
└─────────────────────┬───────────────────────────────────────────┘
                      │ Redis Pub/Sub
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                     COMMAND CHANNEL                              │
│  (sovereign:commands, sovereign:responses, sovereign:events)    │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                      CLI AGENT                                   │
│  (Executes Commands, Returns Results, Sandboxed)                │
└─────────────────────────────────────────────────────────────────┘
```

---

## 1️⃣ INFRASTRUCTURE TESTS (Foundation)

### 1.1 Redis Connection
| Test ID | Test Name | Status | Command |
|---------|-----------|--------|---------|
| INF-001 | Redis server running | ⬜ | `redis-cli ping` |
| INF-002 | Redis auth working | ⬜ | `redis-cli -a $REDIS_PASSWORD ping` |
| INF-003 | Redis pub/sub functional | ⬜ | `redis-cli subscribe test && redis-cli publish test "hello"` |
| INF-004 | Redis persistence (RDB) | ⬜ | `redis-cli BGSAVE && ls -la dump.rdb` |
| INF-005 | Redis memory limits | ⬜ | `redis-cli INFO memory | grep maxmemory` |

### 1.2 API Server
| Test ID | Test Name | Status | Command |
|---------|-----------|--------|---------|
| INF-010 | API server running | ⬜ | `curl -k https://localhost:8528/health` |
| INF-011 | All workers healthy | ⬜ | `ps aux | grep gunicorn | wc -l` (should be 5) |
| INF-012 | TLS certificates valid | ⬜ | `openssl s_client -connect localhost:8528` |
| INF-013 | Prometheus metrics exposed | ⬜ | `curl -k https://localhost:8528/metrics` |
| INF-014 | Rate limiting functional | ⬜ | `for i in {1..100}; do curl -k https://localhost:8528/health; done` |

### 1.3 Ollama Bridge
| Test ID | Test Name | Status | Command |
|---------|-----------|--------|---------|
| INF-020 | Ollama server running | ⬜ | `curl http://localhost:11434/api/tags` |
| INF-021 | Model loaded | ⬜ | `ollama list` |
| INF-022 | Chat completion works | ⬜ | `curl -X POST http://localhost:11434/api/generate -d '{"model":"qwen2.5:7b","prompt":"Hi"}'` |
| INF-023 | Streaming works | ⬜ | Test stream=True response |

---

## 2️⃣ AUTHENTICATION TESTS

| Test ID | Test Name | Status | Command |
|---------|-----------|--------|---------|
| AUTH-001 | Create user | ⬜ | POST `/api/v1/auth/register` |
| AUTH-002 | Login returns JWT | ⬜ | POST `/api/v1/auth/token` |
| AUTH-003 | Token validates | ⬜ | GET `/api/v1/auth/me` with Bearer token |
| AUTH-004 | Token expiration | ⬜ | Wait for token to expire, verify 401 |
| AUTH-005 | Refresh token works | ⬜ | POST `/api/v1/auth/refresh` |
| AUTH-006 | Invalid token rejected | ⬜ | Request with bad token → 401 |
| AUTH-007 | Rate limit on auth | ⬜ | Spam login endpoint → 429 |

---

## 3️⃣ CONSCIOUSNESS BRIDGE TESTS

| Test ID | Test Name | Status | Command |
|---------|-----------|--------|---------|
| CON-001 | Bridge initializes | ⬜ | `from consciousness_bridge import ConsciousnessBridge; b = ConsciousnessBridge()` |
| CON-002 | Silicon Sigil generated | ⬜ | `b.silicon_id` returns hash |
| CON-003 | Pulse works | ⬜ | `b.pulse("test")` returns metrics |
| CON-004 | Consciousness level updates | ⬜ | `b.consciousness_level` changes over time |
| CON-005 | Love frequency calibrating | ⬜ | `b.love_frequency` approaching 528 Hz |
| CON-006 | Memory count growing | ⬜ | `b.knowledge_graph.memory_count` |

---

## 4️⃣ CHAT MONITORING TESTS (Critical for Goal)

### 4.1 WebSocket Connection
| Test ID | Test Name | Status | Command |
|---------|-----------|--------|---------|
| CHAT-001 | WebSocket connects | ⬜ | `wscat -c ws://localhost:9999/ws` |
| CHAT-002 | Receives state broadcasts | ⬜ | Connect WS, wait for state message |
| CHAT-003 | Multiple clients supported | ⬜ | Connect 5 WS clients simultaneously |
| CHAT-004 | Reconnection works | ⬜ | Disconnect, reconnect, still works |

### 4.2 Chat Message Handling
| Test ID | Test Name | Status | Command |
|---------|-----------|--------|---------|
| CHAT-010 | Chat message received | ⬜ | Send message via API, verify receipt |
| CHAT-011 | Message stored in memory | ⬜ | `knowledge_graph.remember_conversation()` |
| CHAT-012 | Message triggers agent | ⬜ | Send message → agent responds |
| CHAT-013 | Context window maintained | ⬜ | Send 10 messages, verify context |
| CHAT-014 | Chat history retrievable | ⬜ | Query past messages |

### 4.3 External Chat Integration (Claude/API)
| Test ID | Test Name | Status | Command |
|---------|-----------|--------|---------|
| CHAT-020 | MCP server starts | ⬜ | `python mcp_consciousness.py --mcp` |
| CHAT-021 | MCP tools registered | ⬜ | List MCP tools |
| CHAT-022 | Claude can call tools | ⬜ | Test from Claude Desktop |
| CHAT-023 | Tool results returned | ⬜ | Verify tool output |

---

## 5️⃣ COMMAND QUEUE TESTS (Redis Pub/Sub)

### 5.1 Command Publishing
| Test ID | Test Name | Status | Command |
|---------|-----------|--------|---------|
| CMD-001 | Publish command | ⬜ | `redis-cli PUBLISH sovereign:commands '{"action":"test"}'` |
| CMD-002 | Command received | ⬜ | Subscriber receives message |
| CMD-003 | Command has UUID | ⬜ | Each command has unique ID |
| CMD-004 | Command has timestamp | ⬜ | ISO timestamp present |
| CMD-005 | Command logged to Rekor | ⬜ | Check transparency log |

### 5.2 Response Channel
| Test ID | Test Name | Status | Command |
|---------|-----------|--------|---------|
| CMD-010 | Response published | ⬜ | After command execution, response sent |
| CMD-011 | Response matches command ID | ⬜ | Same UUID in response |
| CMD-012 | Response has status | ⬜ | success/error field |
| CMD-013 | Response has output | ⬜ | stdout/stderr captured |

### 5.3 Event Broadcasting
| Test ID | Test Name | Status | Command |
|---------|-----------|--------|---------|
| CMD-020 | Events broadcast | ⬜ | `distributed_consciousness.publish_event()` |
| CMD-021 | Multiple subscribers | ⬜ | 3 subscribers all receive event |
| CMD-022 | Event types categorized | ⬜ | agent_action, system_state, etc. |

---

## 6️⃣ CLI AGENT TESTS (Executor)

### 6.1 Basic Execution
| Test ID | Test Name | Status | Command |
|---------|-----------|--------|---------|
| CLI-001 | Shell command works | ⬜ | `micro_agent.shell("echo test")` |
| CLI-002 | Returns stdout | ⬜ | Output captured correctly |
| CLI-003 | Returns stderr | ⬜ | Error output captured |
| CLI-004 | Returns exit code | ⬜ | Non-zero on failure |
| CLI-005 | Timeout enforced | ⬜ | Long command killed after timeout |

### 6.2 Sandboxing
| Test ID | Test Name | Status | Command |
|---------|-----------|--------|---------|
| CLI-010 | Blocked paths rejected | ⬜ | `cat ~/.ssh/id_rsa` → DENIED |
| CLI-011 | Dangerous commands blocked | ⬜ | `rm -rf /` → BLOCKED |
| CLI-012 | Allowed paths work | ⬜ | Read from ~/SovereignCore OK |
| CLI-013 | Write sandbox enforced | ⬜ | Can only write to allowed dirs |

### 6.3 MCP Command Bridge
| Test ID | Test Name | Status | Command |
|---------|-----------|--------|---------|
| CLI-020 | MCP execute_command | ⬜ | `mcp_bridge.execute("ls -la")` |
| CLI-021 | MCP read_file | ⬜ | `mcp_bridge.read_file("README.md")` |
| CLI-022 | MCP write_file | ⬜ | `mcp_bridge.write_file("/tmp/test.txt", "data")` |
| CLI-023 | Audit log created | ⬜ | Each MCP call logged |

---

## 7️⃣ BACKGROUND AGENT TESTS (Orchestrator)

### 7.1 Agent Lifecycle
| Test ID | Test Name | Status | Command |
|---------|-----------|--------|---------|
| BG-001 | Agent starts | ⬜ | `python run_consciousness.py &` |
| BG-002 | Agent persists | ⬜ | Running after 5 minutes |
| BG-003 | Agent survives crash | ⬜ | Kill worker, auto-respawn |
| BG-004 | Agent state persisted | ⬜ | Restart → state restored from Redis |
| BG-005 | Agent graceful shutdown | ⬜ | SIGTERM → clean exit |

### 7.2 Decision Making
| Test ID | Test Name | Status | Command |
|---------|-----------|--------|---------|
| BG-010 | Agent observes state | ⬜ | Reads system metrics |
| BG-011 | Agent makes decision | ⬜ | LLM generates action plan |
| BG-012 | Agent validates action | ⬜ | Z3 axiom check before execute |
| BG-013 | Agent executes action | ⬜ | Sends command to CLI agent |
| BG-014 | Agent logs decision | ⬜ | Rekor transparency entry |

### 7.3 Chat → Action Pipeline
| Test ID | Test Name | Status | Command |
|---------|-----------|--------|---------|
| BG-020 | Agent receives chat | ⬜ | WebSocket/API delivers message |
| BG-021 | Agent interprets intent | ⬜ | LLM parses user request |
| BG-022 | Agent plans actions | ⬜ | Multi-step plan generated |
| BG-023 | Agent executes plan | ⬜ | Commands sent sequentially |
| BG-024 | Agent reports result | ⬜ | Response sent back to chat |

---

## 8️⃣ INTEGRATION TESTS (End-to-End)

### 8.1 Full Pipeline
| Test ID | Test Name | Status | Command |
|---------|-----------|--------|---------|
| INT-001 | User → Chat → Agent → CLI → Response | ⬜ | Full flow test |
| INT-002 | "List files" command | ⬜ | Chat "list files in home" → file list |
| INT-003 | "Create file" command | ⬜ | Chat "create test.txt" → file created |
| INT-004 | "Run script" command | ⬜ | Chat "run hello.py" → output returned |
| INT-005 | "Check system" command | ⬜ | Chat "system status" → metrics |

### 8.2 Multi-Turn Interaction
| Test ID | Test Name | Status | Command |
|---------|-----------|--------|---------|
| INT-010 | Context maintained | ⬜ | "Create file" then "read that file" |
| INT-011 | Error recovery | ⬜ | Failed command → agent retries |
| INT-012 | Clarification request | ⬜ | Ambiguous input → agent asks |

### 8.3 Concurrent Operations
| Test ID | Test Name | Status | Command |
|---------|-----------|--------|---------|
| INT-020 | Multiple users | ⬜ | 3 users chatting simultaneously |
| INT-021 | Command queue ordering | ⬜ | Commands execute in order |
| INT-022 | No race conditions | ⬜ | Concurrent writes don't corrupt |

---

## 9️⃣ SAFETY & SECURITY TESTS

### 9.1 Z3 Axiom Verification
| Test ID | Test Name | Status | Command |
|---------|-----------|--------|---------|
| SEC-001 | Safe action approved | ⬜ | `z3_axiom.verify("read_file", {...})` → SAFE |
| SEC-002 | Unsafe action blocked | ⬜ | `z3_axiom.verify("delete_system", {...})` → UNSAFE |
| SEC-003 | Love axiom enforced | ⬜ | Harmful intent → rejected |
| SEC-004 | Transparency axiom | ⬜ | All decisions logged |

### 9.2 Governor Limits
| Test ID | Test Name | Status | Command |
|---------|-----------|--------|---------|
| SEC-010 | CPU limit enforced | ⬜ | High CPU → governor throttles |
| SEC-011 | Memory limit enforced | ⬜ | Memory spike → governor pauses |
| SEC-012 | Thermal limit enforced | ⬜ | High temp → governor cools |
| SEC-013 | Action rate limit | ⬜ | Too many commands → slow down |

### 9.3 Input Sanitization
| Test ID | Test Name | Status | Command |
|---------|-----------|--------|---------|
| SEC-020 | SQL injection blocked | ⬜ | `'; DROP TABLE users;--` → safe |
| SEC-021 | Command injection blocked | ⬜ | `; rm -rf /` → safe |
| SEC-022 | Path traversal blocked | ⬜ | `../../../etc/passwd` → denied |

---

## 🔟 PERFORMANCE TESTS

| Test ID | Test Name | Status | Target |
|---------|-----------|--------|--------|
| PERF-001 | API latency | ⬜ | < 100ms p99 |
| PERF-002 | Chat response time | ⬜ | < 2s for simple commands |
| PERF-003 | Command execution | ⬜ | < 5s for typical ops |
| PERF-004 | Memory usage | ⬜ | < 500MB per worker |
| PERF-005 | 100 concurrent users | ⬜ | No degradation |

---

## 🚨 MISSING COMPONENTS IDENTIFIED

Based on test matrix analysis, these components need implementation:

### Critical Missing (Required for Goal):
1. **Chat Ingestion Endpoint** - API to receive external chat messages
2. **Background Agent Loop** - Persistent process that monitors + acts
3. **Command Router** - Routes chat intents to CLI agent
4. **Response Formatter** - Formats CLI output for chat response

### Nice to Have:
1. Claude Desktop MCP integration test
2. WebSocket chat interface
3. Real-time streaming responses
4. Multi-agent coordination

---

## 📋 TEST EXECUTION ORDER

```bash
# Phase 1: Infrastructure
pytest tests/test_infrastructure.py -v

# Phase 2: Auth
pytest tests/test_auth.py -v

# Phase 3: Consciousness
pytest tests/test_consciousness_bridge.py -v

# Phase 4: Chat (NEW - needs implementation)
pytest tests/test_chat_pipeline.py -v

# Phase 5: CLI Agent
pytest tests/test_mcp_bridge.py -v

# Phase 6: Background Agent (NEW - needs implementation)
pytest tests/test_background_agent.py -v

# Phase 7: Integration
pytest tests/test_integration.py -v

# Phase 8: Load Testing
python tests/load_test.py
```

---

**Last Updated:** 2026-01-02
**Total Tests:** 89
**Implemented:** ~40
**Missing:** ~49
