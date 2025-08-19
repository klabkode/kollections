const express = require('express');
const path = require('path');
const fs = require('fs').promises; // Use promises for asynchronous operations
const app = express();
const pandoc = require('node-pandoc');
const { exec } = require('child_process');
const PORT = process.env.PORT || 9001;

const BASE_DIR = process.argv[2] || path.resolve(__dirname); // CLI path or default to current directory

// Middleware to serve static files
app.use(express.static(path.join(__dirname, 'public')));

app.get('/api/disk-usage', (req, res) => {
    exec('df -h .', (err, stdout, stderr) => {
        if (err || stderr) {
            console.error('Error fetching disk usage:', err || stderr);
            return res.status(500).json({ error: 'Unable to fetch disk usage' });
        }

        const lines = stdout.split('\n');
        const diskInfo = lines[1].split(/\s+/);  // Extract data from the second line

        res.json({
            filesystem: diskInfo[0],
            size: diskInfo[1],
            used: diskInfo[2],
            available: diskInfo[3],
            usePercentage: diskInfo[4],
            mountedOn: diskInfo[5]
        });
    });
});

// Helper function to prevent path traversal attacks
function sanitizePath(requestPath) {
    const resolvedPath = path.resolve(BASE_DIR, requestPath);
    if (!resolvedPath.startsWith(BASE_DIR)) {
        throw new Error('Invalid path');
    }
    return resolvedPath;
}

// Helper function to check if a path is a symlinked directory and resolve it
async function resolveIfSymlinkedDir(filePath) {
    try {
        const stats = await fs.lstat(filePath);
        if (stats.isSymbolicLink()) {
            const realPath = await fs.realpath(filePath);
            return await fs.stat(realPath);
        }
        return stats;
    } catch (err) {
        console.error('Error resolving symlink:', err);
        throw err;
    }
}

// API to list directory contents
app.get('/api/files', async (req, res) => {
    try {
        const reqPath = path.join(BASE_DIR, decodeURIComponent(req.query.path));
        const dirPath = sanitizePath(reqPath);
        const files = await fs.readdir(dirPath, { withFileTypes: true });

        //console.log(`dirPath=${dirPath}`);

        const fileDetails = await Promise.all(files.map(async (file) => {
            const filePath = path.join(dirPath, file.name);

            // Check for symlink and resolve if necessary
            const stats = await resolveIfSymlinkedDir(filePath);
            const isDirectory = stats.isDirectory();
            const nItems = isDirectory ? (await fs.readdir(filePath)).length : 0;

            return {
                name: file.name,
                path: filePath.replace(BASE_DIR, ''),
                isdir: isDirectory,
                nitems: nItems,
                size: isDirectory ? '0' : (stats.size / (1024 * 1024)).toFixed(2) + ' MB',
                modtime: stats.mtime.toLocaleString(),
            };
        }));

        res.json(fileDetails);
    } catch (err) {
        console.error('Error retrieving files:', err);
        res.status(500).json({ error: 'Unable to scan directory' });
    }
});

function DXR_StreamFile(filePath) {
    return new Promise((resolve, reject) => {
        const dexCmd = `DXR_ -n -p ${filePath}`;

        //console.log(`dexCmd=${dexCmd}`);

        exec(dexCmd, (error) => {
            if (error) {
                reject(new Error(`Exec failed for '${filePath}'`));
            } else {
                resolve(`Streaming ... ${filePath}`);
            }
        });
    });
}

function xdgOpen(filePath) {
    return new Promise((resolve, reject) => {
        const xdgCmd = `xdg-open ${filePath}`;

        exec(xdgCmd, (error) => {
            if (error) {
                reject(new Error(`xdgExec failed for '${filePath}'`));
            } else {
                resolve(`Streaming ... ${filePath}`);
            }
        });
    });
}

// API to view or download a file
app.get('/api/file', async (req, res) => {
    try {
        const _filePath = path.join(BASE_DIR, req.query.path);
        const filePath = sanitizePath(_filePath);

        //console.log(`filePath=${filePath}`);

        const stats = await resolveIfSymlinkedDir(filePath);
        if (!stats.isFile()) {
            return res.status(404).send('File not found');
        }

        // Determine the file extension
        const extname = path.extname(filePath).toLowerCase();
        const imageExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp'];
        const audioExtensions = ['.mp3', '.wav', '.ogg', '.aac', '.flac', '.m4a'];
        const videoExtensions = ['.mp4', '.webm', '.ogg', '.avi', '.mkv'];
        const dexfileExtensions = ['.dex', '.sxi', '.sxa', '.sxv'];
        const pdffileExtensions = ['.pdf'];
        const docfileExtensions = ['.doc', '.docx'];
        const xdgfileExtensions = ['.ppt', '.pptx', '.xls', '.xlsx', '.tgz', '.tar', '.zip', '.gz'];

        //console.log(`extname=${extname}`);

        // Set appropriate Content-Type
        if (imageExtensions.includes(extname)) {
            res.type(extname); // Set appropriate Content-Type for images
            const data = await fs.readFile(filePath); // Read binary data
            return res.send(data); // Send the binary data
        } else if (audioExtensions.includes(extname)) {
            res.type(extname); // Set appropriate Content-Type for audio
            const data = await fs.readFile(filePath); // Read binary data
            return res.send(data); // Send the binary data
        } else if (videoExtensions.includes(extname)) {
            res.type(extname); // Set appropriate Content-Type for video
            const data = await fs.readFile(filePath); // Read binary data
            return res.send(data); // Send the binary data
        } else if (dexfileExtensions.includes(extname)) {
            //console.log(`dexFile=${filePath}`);
            DXR_StreamFile(filePath);
            res.status(250).send('Streaming...');
        } else if (pdffileExtensions.includes(extname)) {
            res.type(extname);
            const data = await fs.readFile(filePath);
            return res.send(data);
        } else if (docfileExtensions.includes(extname)) {
            // Set your callback function
            callback = function (err, result) {
                if (err) {
                    console.error('pandoc() failed: ', err);
                } else {
                    // Without the -o arg, the converted value will be returned.
                    //console.log(result), result;
                    //res.type(extname);
                    return res.send(result);
                }
            };

            pandoc(filePath, '-t html', callback);
        } else if (xdgfileExtensions.includes(extname)) {
            xdgOpen(filePath);
            res.status(250).send('Streaming...');
        } else {
            const data = await fs.readFile(filePath, 'utf8'); // Read as UTF-8 for text files
            res.type(extname); // Set appropriate Content-Type for text files
            return res.send(data); // Send the text data
        }
    } catch (err) {
        console.error('Error reading file:', err);
        if (err.code === 'ENOENT') {
            return res.status(404).send('File not found');
        }
        res.status(500).send('Unable to read file');
    }
});

// Error handling middleware
app.use((err, req, res, next) => {
    console.error('Error occurred:', err);
    res.status(500).json({ error: err.message || 'An error occurred' });
});

// Start the server
app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
    console.log(`Serving files from: ${BASE_DIR}`);
});
