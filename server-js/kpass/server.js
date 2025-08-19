/* Kpass web server */

const express  = require('express');
const process  = require('process');
const readline = require('readline');
const { exec } = require('child_process');

const app = express();
const port = 9002;

// Call kpass_main to ensure the KEY is set
kpass_main().then(() => {
    // Middleware and routes
    app.use(express.json());
    app.use(express.static('public'));

    function kpass_exec(command, res) {
        console.log(`Exec: ${command}`);

        exec(command, (error, stdout, stderr) => {
            if (error) {
                console.error(`Execution error: ${error.message}`);
                return res.status(500).json({ error: error.message });
            }

            //if (stdout) {
            //    console.error(`${stdout}`);
            //}

            if (stderr) {
                console.error(`stderr: ${stderr}`);
                return res.status(500).json({ error: stderr });
            }

            res.send(stdout || stderr);
        });
    }

    // Endpoint to fetch the list of domains
    app.get('/list', (req, res) => {
        kpass_exec(`kpass -j -n -L`, res);
    });

    // POST endpoint to handle clicking on a domain entry
    app.post('/domain', (req, res) => {
        const domain = req.body.domain;

        if (!domain) {
            return res.status(400).json({ error: 'Domain name is required' });
        }

        //console.log(`\nReceived domain: ${domain}`);

        kpass_exec(`kpass -j -f 'NAME=${domain}'`, res);
    });

    // POST endpoint to handle clicking on a domain entry
    app.post('/grep', (req, res) => {
        const query = req.body.query;

        if (!query) {
            return res.status(400).json({ error: 'Search pattern is required' });
        }

        //console.log(`\nReceived query: ${query}`);

        kpass_exec(`kpass -j -g '${query}'`, res);
    });

    // POST endpoint to receive entry_id
    app.post('/entry', (req, res) => {
        const entry_id = req.body.entry_id;

        if (entry_id === undefined) {
            return res.status(400).json({ error: 'Entry ID is required' });
        }

        //console.log(`\nReceived entry_id: ${entry_id}`);

        kpass_exec(`kpass -j -l ${entry_id}`, res);
    });

    // Route to handle fetching an entry by ID
    app.get('/entry/:id', (req, res) => {
        const entry_id = req.params.id;

        if (!entry_id) {
            return res.status(400).json({ error: 'Entry ID is required' });
        }

        //console.log(`\nReceived entry_id: ${entry_id}`);

        kpass_exec(`kpass -j -l ${entry_id}`, res);
    });

    // 404 Error handling
    app.use((req, res, next) => {
        res.status(404).json({ error: '404: Not Found' });
    });

    // Error handling middleware for other types of errors
    app.use((err, req, res, next) => {
        console.error('Error:', err.stack);
        res.status(500).json({ error: '500: Server Error' });
    });

    // Start the server
    app.listen(port, () => {
        console.log(`Server running on http://localhost:${port}`);
    });
});

// Function to prompt for master key
function kpass_read_master_key() {
    return new Promise((resolve, reject) => {
        const rl = readline.createInterface({
            input: process.stdin,
            output: process.stdout
        });

        rl.question('Enter master key: ', (answer) => {
            rl.close();
            if (!answer) {
                reject(new Error('Master key is required.'));
            } else {
                resolve(answer);
            }
        });
    });
}

// Function to initialize the master key
async function kpass_main() {
    if (!process.env.KPASS_MASTER_KEY) {
        try {
            const masterKey = await kpass_read_master_key();
            process.env.KPASS_MASTER_KEY = masterKey;
        } catch (error) {
            console.error(error.message);
            process.exit(1);
        }
    }
}

/* EOF */
