use actix_web::{App, HttpResponse, HttpServer, Responder, get, post, web};
use serde::{Deserialize, Serialize};
use std::fs;
use std::io::Write;
use std::sync::Mutex;

mod traits;
mod governance;
mod panopticon;
use governance::fuel::FuelToken;
use governance::auction::{AuctionHouse, Bid};

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
    auction_house: Mutex<AuctionHouse>,
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

// --- Fuel Endpoints ---

// --- Governance Endpoints ---
use governance::constitution::Constitution;
use traits::sovereign_agent::Thought;

#[post("/governance/audit")]
async fn audit_thought_handler(thought: web::Json<Thought>) -> impl Responder {
    let approved = Constitution::verify_axiomatic_barrier(&thought);
    
    if approved {
        println!("[SUPREME COURT] Thought Approved: {:.2} confidence", thought.confidence);
        HttpResponse::Ok().json(true)
    } else {
        println!("[SUPREME COURT] VETOED: Axiomatic Violation!");
        HttpResponse::Forbidden().body("Violation of Constitution 1.2")
    }
}

// --- Auction Endpoints ---

#[post("/governance/auction/bid")]
async fn place_bid_handler(data: web::Data<AppState>, bid: web::Json<Bid>) -> impl Responder {
    let mut ah = data.auction_house.lock().unwrap();
    ah.place_bid(bid.into_inner());
    println!("[AUCTION] Bid Placed. Total Bids: {}", ah.current_bids.len());
    HttpResponse::Ok().body("Bid Accepted")
}

#[derive(Deserialize)]
struct FinalizeRequest {
    slots: usize,
}

#[post("/governance/auction/finalize")]
async fn finalize_auction_handler(data: web::Data<AppState>, req: web::Json<FinalizeRequest>) -> impl Responder {
    let mut ah = data.auction_house.lock().unwrap();
    let winners = ah.finalize_auction(req.slots);
    println!("[AUCTION] Auction Closed. Winners: {:?}", winners);
    HttpResponse::Ok().json(winners)
}

// --- Watchdog Endpoints ---

#[derive(Serialize)]
struct WatchdogStatus {
    status: String,
    akashic_memories: usize,
    auction_bids: usize,
    constitution_valid: bool,
}

#[get("/watchdog/status")]
async fn watchdog_status_handler(data: web::Data<AppState>) -> impl Responder {
    let record = data.akashic_record.lock().unwrap();
    let ah = data.auction_house.lock().unwrap();
    
    // TODO: Actual Constitution::audit_system() would need agent list
    // For now, we return "true" if system is responsive
    let status = WatchdogStatus {
        status: "OBSERVING".to_string(),
        akashic_memories: record.len(),
        auction_bids: ah.current_bids.len(),
        constitution_valid: true, // Placeholder until full agent integration
    };
    
    println!("[WATCHDOG] Status Check. Memories: {}, Bids: {}", status.akashic_memories, status.auction_bids);
    HttpResponse::Ok().json(status)
}

// --- External API (Public-Facing) ---

#[derive(Serialize)]
struct SystemOverview {
    version: String,
    endpoints: Vec<String>,
    akashic_count: usize,
    constitution_status: String,
}

#[get("/api/v1/overview")]
async fn api_overview_handler(data: web::Data<AppState>) -> impl Responder {
    let record = data.akashic_record.lock().unwrap();
    
    let overview = SystemOverview {
        version: "5.0.0".to_string(),
        endpoints: vec![
            "/health".to_string(),
            "/infer".to_string(),
            "/remember".to_string(),
            "/recall".to_string(),
            "/fuel/issue".to_string(),
            "/fuel/spend".to_string(),
            "/governance/audit".to_string(),
            "/governance/auction/bid".to_string(),
            "/governance/auction/finalize".to_string(),
            "/watchdog/status".to_string(),
            "/api/v1/overview".to_string(),
        ],
        akashic_count: record.len(),
        constitution_status: "ACTIVE".to_string(),
    };
    
    HttpResponse::Ok().json(overview)
}

#[derive(Deserialize)]
struct IssueFuelRequest {
    owner_id: String,
    amount: f64,
}

#[post("/fuel/issue")]
async fn issue_fuel_handler(req: web::Json<IssueFuelRequest>) -> impl Responder {
    let token = FuelToken::new(&req.owner_id, req.amount);
    println!("[TREASURY] Minting Fuel for {}: {}", req.owner_id, req.amount);
    HttpResponse::Ok().json(token)
}

#[derive(Deserialize)]
struct SpendFuelRequest {
    token: FuelToken,
    cost: f64,
}

#[post("/fuel/spend")]
async fn spend_fuel_handler(req: web::Json<SpendFuelRequest>) -> impl Responder {
    // we need a mutable token, so we clone it from the request
    let mut token = req.token.clone();
    
    if let Err(e) = token.spend(req.cost) {
        println!("[TREASURY] Spend Refused: {}", e);
        return HttpResponse::BadRequest().body(e);
    }
    println!("[TREASURY] {} Spent Fuel: {}", token.owner_id, req.cost);
    HttpResponse::Ok().json(token)
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
        auction_house: Mutex::new(AuctionHouse::new()),
    });

    HttpServer::new(move || {
        App::new()
            .app_data(app_state.clone())
            .service(health_handler)
            .service(infer_handler)
            .service(collapse_handler)
            .service(remember_handler)
            .service(recall_handler)
            .service(issue_fuel_handler)
            .service(spend_fuel_handler)
            .service(audit_thought_handler)
            .service(place_bid_handler)
            .service(finalize_auction_handler)
            .service(watchdog_status_handler)
            .service(api_overview_handler)
    })
    .bind(("0.0.0.0", 9000))?
    .run()
    .await
}
