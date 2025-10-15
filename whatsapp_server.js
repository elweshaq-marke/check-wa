const { default: makeWASocket, DisconnectReason, useMultiFileAuthState, fetchLatestBaileysVersion, makeCacheableSignalKeyStore } = require('@whiskeysockets/baileys');
const express = require('express');
const multer = require('multer');
const fs = require('fs');
const path = require('path');
const qrcode = require('qrcode-terminal');

const app = express();
const upload = multer({ dest: 'uploads/' });

let sock = null;
let qrCodeData = null;
let pairingCode = null;
let isConnected = false;

app.use(express.json());

async function connectToWhatsApp(sessionPath = './auth_info_baileys') {
    const { state, saveCreds } = await useMultiFileAuthState(sessionPath);
    const { version } = await fetchLatestBaileysVersion();

    sock = makeWASocket({
        version,
        auth: {
            creds: state.creds,
            keys: makeCacheableSignalKeyStore(state.keys, require('pino')({ level: 'silent' })),
        },
        printQRInTerminal: false,
        browser: ['WhatsApp Checker', 'Chrome', '1.0.0'],
    });

    sock.ev.on('connection.update', async (update) => {
        const { connection, lastDisconnect, qr } = update;

        if (qr) {
            qrCodeData = qr;
            console.log('QR Code received');
        }

        if (connection === 'close') {
            const shouldReconnect = lastDisconnect?.error?.output?.statusCode !== DisconnectReason.loggedOut;
            console.log('Connection closed, reconnecting:', shouldReconnect);
            isConnected = false;
            
            if (shouldReconnect) {
                await connectToWhatsApp(sessionPath);
            }
        } else if (connection === 'open') {
            console.log('WhatsApp connection opened successfully');
            isConnected = true;
            qrCodeData = null;
            pairingCode = null;
        }
    });

    sock.ev.on('creds.update', saveCreds);

    return sock;
}

async function checkNumber(phoneNumber) {
    if (!sock || !isConnected) {
        throw new Error('WhatsApp not connected');
    }

    try {
        const formattedNumber = phoneNumber.includes('@') ? phoneNumber : `${phoneNumber}@s.whatsapp.net`;
        const [result] = await sock.onWhatsApp(formattedNumber.replace('@s.whatsapp.net', ''));
        
        if (result && result.exists) {
            return { registered: true, jid: result.jid };
        } else {
            return { registered: false };
        }
    } catch (error) {
        console.error('Error checking number:', error);
        throw error;
    }
}

async function requestPairingCode(phoneNumber) {
    if (!sock) {
        throw new Error('WhatsApp socket not initialized');
    }

    try {
        const code = await sock.requestPairingCode(phoneNumber);
        pairingCode = code;
        console.log('Pairing code generated:', code);
        return code;
    } catch (error) {
        console.error('Error generating pairing code:', error);
        throw error;
    }
}

app.post('/upload-session', upload.single('session'), async (req, res) => {
    try {
        if (!req.file) {
            return res.status(400).json({ error: 'No session file uploaded' });
        }

        const sessionPath = './auth_info_baileys';
        
        if (!fs.existsSync(sessionPath)) {
            fs.mkdirSync(sessionPath, { recursive: true });
        }

        const uploadedPath = req.file.path;
        const targetPath = path.join(sessionPath, 'creds.json');
        
        fs.copyFileSync(uploadedPath, targetPath);
        fs.unlinkSync(uploadedPath);

        await connectToWhatsApp(sessionPath);

        res.json({ success: true, message: 'Session uploaded and connected' });
    } catch (error) {
        console.error('Error uploading session:', error);
        res.status(500).json({ error: error.message });
    }
});

app.post('/create-session', async (req, res) => {
    try {
        const { phoneNumber } = req.body;
        
        if (!phoneNumber) {
            return res.status(400).json({ error: 'Phone number is required' });
        }

        const sessionPath = './auth_info_baileys';
        
        if (!fs.existsSync(sessionPath)) {
            fs.mkdirSync(sessionPath, { recursive: true });
        }

        await connectToWhatsApp(sessionPath);

        const code = await requestPairingCode(phoneNumber);

        res.json({ success: true, pairingCode: code });
    } catch (error) {
        console.error('Error creating session:', error);
        res.status(500).json({ error: error.message });
    }
});

app.post('/check-number', async (req, res) => {
    try {
        const { phoneNumber } = req.body;
        
        if (!phoneNumber) {
            return res.status(400).json({ error: 'Phone number is required' });
        }

        const result = await checkNumber(phoneNumber);

        if (result.registered) {
            res.json({ status: 'registered', number: phoneNumber });
        } else {
            res.json({ status: 'not registered', number: phoneNumber });
        }
    } catch (error) {
        console.error('Error checking number:', error);
        res.status(500).json({ error: error.message });
    }
});

app.get('/status', (req, res) => {
    res.json({ 
        connected: isConnected,
        hasQR: !!qrCodeData,
        hasPairingCode: !!pairingCode
    });
});

app.get('/qr', (req, res) => {
    if (qrCodeData) {
        res.json({ qr: qrCodeData });
    } else {
        res.status(404).json({ error: 'No QR code available' });
    }
});

app.get('/pairing-code', (req, res) => {
    if (pairingCode) {
        res.json({ code: pairingCode });
    } else {
        res.status(404).json({ error: 'No pairing code available' });
    }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`WhatsApp server running on port ${PORT}`);
});
