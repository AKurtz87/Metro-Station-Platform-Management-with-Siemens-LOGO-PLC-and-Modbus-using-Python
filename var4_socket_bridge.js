const zmq = require("zeromq/v5-compat"); // Supporto per le API di ZeroMQ 5

const WebSocket = require("ws"); // Modulo WebSocket
const http = require("http"); // Modulo HTTP

// Configurazione del server HTTP per servire la pagina HTML
const server = http.createServer((req, res) => {
  res.writeHead(200, { "Content-Type": "text/html" });
  res.end(`
  <!DOCTYPE html>
  <html>
    <head>
      <title>Stazione dei Treni - Stato in Tempo Reale</title>
      <style>
        body {
          font-family: Arial, sans-serif;
          background-color: #f4f4f9;
          color: #333;
          margin: 0;
          padding: 0;
          display: flex;
          flex-direction: column;
          align-items: center;
        }
        h1 {
          margin: 20px 0;
          font-size: 2.5rem;
          color: black;
        }
        .platform-container {
          display: grid;
          grid-template-areas:
            "bin4 bin1"
            "bin3 bin2";
          gap: 20px;
          width: 80%;
          max-width: 800px;
          margin-bottom: 20px;
        }
        .platform {
          background: #fff;
          border: 2px solid black;
          border-radius: 8px;
          padding: 20px;
          box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
          text-align: center;
          transition: transform 0.2s, box-shadow 0.2s;
          min-width: 350px;
        }

        .platform h2 {
          font-size: 1.5rem;
          color: #333;
        }
        .platform .status {
          font-size: 2rem;
          margin: 10px 0;
          font-weight: bold;
        }
        .platform.idle {
          border-color: black;
          background: lightgray;
        }
        .platform.arriving {
          border-color: black;
          background: yellow;
        }
        .platform.stopped {
          border-color: black;
          background: darkorange;
        }
        .platform.ready_to_depart {
          border-color: black;
          background: greenyellow;
        }
        .platform.departing {
          border-color: black;
          background: deepskyblue;
        }
        #platform-4 {
          grid-area: bin4;
        }
        #platform-1 {
          grid-area: bin1;
        }
        #platform-3 {
          grid-area: bin3;
        }
        #platform-2 {
          grid-area: bin2;
        }
      </style>
    </head>
    <body>
      <h1>Stazione 4B</h1>
      <div class="platform-container" id="platforms">
        <div id="platform-4" class="platform"></div>
        <div id="platform-1" class="platform"></div>
        <div id="platform-3" class="platform"></div>
        <div id="platform-2" class="platform"></div>
      </div>
      <script>
        const ws = new WebSocket("ws://localhost:8080");
  
        // Mappa degli stati per assegnare classi CSS
        const statusClasses = {
          idle: "idle",
          arriving: "arriving",
          stopped: "stopped",
          ready_to_depart: "ready_to_depart",
          departing: "departing",
        };
  
        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data); // Interpreta il JSON
  
            // Variabile per tenere traccia dei binari autorizzati alla partenza
            let readyToDepartCount = 0;
  
            // Aggiorna ogni piattaforma in base ai dati
            data.trains.forEach((train) => {
              const platformDiv = document.getElementById(\`platform-\${train.platform}\`);
              platformDiv.className = "platform " + (statusClasses[train.status] || "idle");
              platformDiv.innerHTML = \`
                <h2>Binario \${train.platform}</h2>
                <div class="status">\${train.status}</div>
              \`;
  
              // Incrementa il contatore se il binario è in stato "ready_to_depart"
              if (train.status === "ready_to_depart") {
                readyToDepartCount++;
              }
            });
  
          } catch (err) {
            console.error("Errore nel parsing del JSON:", err);
          }
        };
      </script>
    </body>
  </html>
    `);
});

// Avvia il server HTTP sulla porta 3000
server.listen(3000, () => {
  console.log("Server HTTP in ascolto su http://localhost:3000");
});

// Configurazione del server WebSocket
const wss = new WebSocket.Server({ port: 8080 });
console.log("WebSocket server in ascolto su ws://localhost:8080");

// Configurazione del socket ZeroMQ per la sottoscrizione
const sock = zmq.socket("sub");
sock.connect("tcp://localhost:5556"); // Si connette al publisher Python
sock.subscribe(""); // Si sottoscrive a tutti i messaggi
console.log("Subscriber ZeroMQ connesso a tcp://localhost:5556");

// Quando ZeroMQ riceve un messaggio
sock.on("message", (message) => {
  try {
    // Tenta di interpretare il messaggio come JSON
    const data = JSON.parse(message.toString());

    // Invia il JSON ai client WebSocket
    wss.clients.forEach((client) => {
      if (client.readyState === WebSocket.OPEN) {
        client.send(JSON.stringify(data)); // Converti il JSON in stringa prima di inviarlo
      }
    });
  } catch (err) {
    console.error("Errore nel parsing del messaggio come JSON:", err);

    // Invia il messaggio originale come fallback
    wss.clients.forEach((client) => {
      if (client.readyState === WebSocket.OPEN) {
        client.send(message.toString());
      }
    });
  }
});
