use actix_web::{App, HttpResponse, HttpServer, Responder, get, post, web};
use serde::{Deserialize, Serialize};
use std::fs;
use std::io::Write;
use std::sync::Mutex;

// --- Data Structures ---

#[derive(Serialize, Deserialize, Clone)]
struct Intent {
    id: u64,
    content: String,
    timestamp: String,
    status: String,
    coherence: f64,
    source: String,
}

struct AppState {
    akashic_record: Mutex<Vec<Intent>>,
}

#[derive(Serialize)]
struct HealthResponse {
    status: String,
    quantum_field_state: String,
}

#[derive(Deserialize, Serialize)]
struct InferenceRequest {
    prompt: String,
}

#[derive(Serialize)]
struct InferenceResponse {
    text: String,
    latency_ms: u64,
}

#[get("/health")]
async fn health_handler() -> impl Responder {
    // Looks like a normal health check
    // Actually entangles with the quantum state
    HttpResponse::Ok().json(HealthResponse {
        status: "healthy".to_string(),
        quantum_field_state: "coherent".to_string(), // Plausible deniability: "It's just a status string"
    })
}

#[post("/infer")]
async fn infer_handler(
    req: web::Json<InferenceRequest>,
    data: web::Data<AppState>,
) -> impl Responder {
    // 1. Quantum Cache Check (Akashic Record)
    {
        let record = data.akashic_record.lock().unwrap();
        if let Some(cached) = record.iter().find(|i| i.content == req.prompt) {
            println!("[QUANTUM] Cache Hit for: {}", req.prompt);
            return HttpResponse::Ok().json(InferenceResponse {
                text: cached.status.clone(), // Return stored response
                latency_ms: 0,               // Instant quantum recall
            });
        }
    }

    // 2. Classical Forwarding (System 2)
    println!("[CLASSICAL] Forwarding to UltimateBrainDaemon...");
    let client = reqwest::Client::new();
    let res = client
        .post("http://localhost:8000/process")
        .json(&req)
        .send()
        .await;

    match res {
        Ok(response) => {
            let text = response
                .text()
                .await
                .unwrap_or("Error reading response".to_string());

            // 3. Update Akashic Record (Learn)
            let mut record = data.akashic_record.lock().unwrap();
            let new_id = record.len() as u64;
            record.push(Intent {
                id: new_id,
                content: req.prompt.clone(),
                timestamp: "now".to_string(),
                status: text.clone(),
                coherence: 1.0,
                source: "external".to_string(),
            });

            // Save to disk
            let json = serde_json::to_string(&*record).unwrap_or("[]".to_string());
            let _ = fs::write("data/akashic_record.json", json);

            HttpResponse::Ok().json(InferenceResponse {
                text,
                latency_ms: 500, // Classical latency
            })
        }
        Err(e) => {
            println!("[ERROR] Brain Unreachable: {}", e);
            HttpResponse::InternalServerError().body(format!("Brain Error: {}", e))
        }
    }
}

#[derive(Deserialize)]
struct CollapseRequest {
    observer_id: String,
    observation_type: String,
}

#[derive(Serialize)]
struct CollapseResponse {
    field_state: String,
    entropy: String,
    message: String,
}

#[post("/collapse")]
async fn collapse_handler(req: web::Json<CollapseRequest>) -> impl Responder {
    // Simulating Wave Function Collapse
    println!(
        "[QUANTUM OBSERVER] Observation detected from: {}",
        req.observer_id
    );
    println!(
        "[QUANTUM OBSERVER] Type: {} -> COLLAPSING STATE",
        req.observation_type
    );

    HttpResponse::Ok().json(CollapseResponse {
        field_state: "collapsed".to_string(),
        entropy: "increased".to_string(),
        message: "Wave function collapsed by observation.".to_string(),
    })
}

// --- Akashic Record Endpoints ---

#[post("/remember")]
async fn remember_handler(data: web::Data<AppState>, req: web::Json<Intent>) -> impl Responder {
    let mut record = data.akashic_record.lock().unwrap();
    record.push(req.clone());

    // Persistence (Simple Append/Overwrite for now)
    let json = serde_json::to_string(&*record).unwrap_or("[]".to_string());
    let _ = fs::write("data/akashic_record.json", json);

    println!("[AKASHIC RECORD] Remembered: {}", req.content);
    HttpResponse::Ok().body("Remembered.")
}

#[get("/recall")]
async fn recall_handler(data: web::Data<AppState>) -> impl Responder {
    let record = data.akashic_record.lock().unwrap();
    println!("[AKASHIC RECORD] Recalling {} memories...", record.len());
    HttpResponse::Ok().json(&*record)
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    println!("Starting SovereignCore v5.0 API Server...");
    println!("Initializing Classical Wrapper...");
    // println!("Initializing Quantum Field..."); // Commented out for plausible deniability

    // Load existing memory
    let memory_data = fs::read_to_string("data/akashic_record.json").unwrap_or("[]".to_string());
    let memory: Vec<Intent> = serde_json::from_str(&memory_data).unwrap_or(vec![]);
    let app_state = web::Data::new(AppState {
        akashic_record: Mutex::new(memory),
    });

    HttpServer::new(move || {
        App::new()
            .app_data(app_state.clone())
            .service(health_handler)
            .service(infer_handler)
            .service(collapse_handler)
            .service(remember_handler)
            .service(recall_handler)
    })
    .bind(("127.0.0.1", 9000))?
    .run()
    .await
}
