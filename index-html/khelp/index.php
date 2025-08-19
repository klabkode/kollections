<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <title>Khelp</title>
    <link rel="icon" href="html/favicon.ico" type="image/png">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href='https://fonts.googleapis.com/css?family=Anta' rel='stylesheet'>
    <link href='https://fonts.googleapis.com/css?family=Roboto' rel='stylesheet'>

    <style>
        :root {
            --main-bg-color: #121212;
            --item-hover-color: #212121;
            --main-text-color: lightgray;
        }

        body {
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            color: var(--main-text-color);
            font-family: 'Roboto';
            font-size: 14px;
            background-color: var(--main-bg-color);
        }

        .layout {
            display: flex;
            flex-direction: row;
            height: 100vh;
            width: 100vw;
            overflow: hidden;
        }

        .sidebar {
            width: 20%;
            padding: 10px;
            min-width: 300px;
            max-width: 600px;
            overflow-y: auto;
            background-color: var(--main-bg-color);
            border-right: 1px solid #2c2c2c;
        }

        .main-view {
            flex-grow: 1;
            height: 100%;
        }

        .main-view iframe {
            width: 100%;
            height: 100%;
            border: none;
        }

        @media (max-width: 768px) {
            .layout {
                flex-direction: column;
            }

            .sidebar {
                width: 95%;
                height: auto;
                border-right: none;
                border-bottom: 1px solid #2c2c2c;
            }

            .main-view {
                height: auto;
            }

            .main-view iframe {
                display: none;
            }
        }

        .banner {
            width: 100%;
            position: sticky;
            top: 0;
            z-index: 1000;
            background-color: var(--main-bg-color);
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .search {
            flex-grow: 1;
            max-width: 60%;
            margin-left: 20px;
        }

        .search input {
            width: 100%;
            border: none;
            padding: 12px;
            font-size: 15px;
            color: var(--main-text-color);
            border-radius: 50px;
            box-sizing: border-box;
            transition: all 0.3s ease;
            background-color: #2c2c2c;
        }

        .search input:focus {
            outline: 1px solid var(--item-hover-color);
        }

        .file-item {
            display: flex;
            padding-top: 10px;
            padding-left: 10px;
            padding-bottom: 10px;
            font-weight: bold;
            align-items: center;
            color: var(--main-text-color);
            border-bottom: 1px solid #2c2c2c;
        }

        .file-item:hover {
            border: 1px solid #2c2c2c;
            background-color: var(--item-hover-color);
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2);
        }

        .folder .file-name {
            font-weight: bold;
        }

        .file .file-name {
            font-weight: lighter;
        }

        .file-icon {
            width: 40px;
            height: 40px;
            margin-right: 20px;
        }

        .file-details {
            flex-grow: 1;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .file-name {
            font-size: 18px;
            color: var(--main-text-color);
        }

        .file-more {
            width: 40px;
            height: 40px;
            color: var(--item-hover-color);
            display: flex;
            justify-content: center;
            align-items: center;
            text-align: center;
            cursor: pointer;
            border-radius: 50%;
            border: none;
        }

        .file-more:hover {
            border-radius: 50%;
            border: 2px solid var(--item-hover-color);
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2);
        }

        .collapsed {
            display: none;
        }

        .folder.open+.file-list {
            display: block;
        }

        .folder-container {
            margin: 0px;
        }

        .folder.open,
        .folder.open+.file-list {
            background-color: #2c2c2c;
            border-bottom: 2px solid var(--item-hover-color);
        }

        ul {
            list-style-type: none;
            padding-left: 0;
            margin-top: 0;
            border-radius: 10px;
            overflow: hidden;
        }

        li:first-child .file-item {
            border-top-left-radius: 10px;
            border-top-right-radius: 10px;
        }

        li:last-child .file-item {
            border-bottom-left-radius: 10px;
            border-bottom-right-radius: 10px;
        }

        /* For thin scroll bars */
        /* Chrome, Edge, Safari */
        ::-webkit-scrollbar {
            width: 3px;
            height: 3px;
        }

        ::-webkit-scrollbar-track {
            background: transparent;
        }

        ::-webkit-scrollbar-thumb {
            background-color: #555;
            border-radius: 5px;
        }

        /* Firefox */
        * {
            scrollbar-width: thin;
            scrollbar-color: #555 transparent;
        }
    </style>
</head>

<body>
    <div class="layout">
        <div class="sidebar">
            <div class="banner">
                <h1 style="font-family: 'Anta';font-size: 35px; font-weight: normal;">Khelp</h1>
                <div class="search">
                    <input type="text" id="search-box" placeholder="Search khelp ..." onkeyup="searchFiles()">
                </div>
            </div>
            <div id="card-container">
                <?php
                function listDirectory($dir, $isRoot = false) {
                    $items = scandir($dir);
                    $items = array_diff($items, ['.', '..']);  // Exclude . and ..

                    foreach ($items as $item) {
                        $fullPath = "$dir/$item";

                        if (is_dir($fullPath)) {
                            echo "<ul class='folder-container'>";
                            echo "  <div class='file-item folder' onclick='toggleFolder(this)'>";
                            createTagEntry($fullPath, true);
                            echo "  </div>";
                            echo "  <div class='file-list collapsed'>";
                            listDirectory($fullPath);
                            echo "  </div>";
                            echo "</ul>";
                        } else if (!$isRoot) {
                            echo "<div class='file-item file' onclick='openFile(\"$fullPath\")'>";
                            createTagEntry($fullPath, false);
                            echo "</div>";
                        }
                    }
                }

                function createTagEntry($entryPath, $isFolder) {
                    $entryName = basename($entryPath);
                    $entryIcon = $isFolder ? 'html/book.png' : 'html/page.png';

                    echo "<img src='$entryIcon' class='file-icon'>";
                    echo "<div class='file-details'>";
                    echo "<div class='file-name'>$entryName</div>";
                    echo "</div>";
                }

                $dirTags = 'tags';

                if (is_dir($dirTags)) {
                    listDirectory($dirTags, true);
                } else {
                    echo "<p style='color: orange'>Oops! no tags are there.</p>";
                }
                ?>
            </div>
        </div>
        <div class="main-view">
            <iframe id="file-viewer" name="file-viewer" src="html/tagview.html" frameborder="0"></iframe>
        </div>
    </div>
    <script>
        function toggleFolder(folderItem) {
            const allFolders = document.querySelectorAll('.folder.open');
            allFolders.forEach(openFolder => {
                if (openFolder !== folderItem) {
                    openFolder.classList.remove('open');
                    openFolder.nextElementSibling.classList.add('collapsed');
                    openFolder.parentNode.classList.remove('open');
                }
            });

            const sublist = folderItem.nextElementSibling;
            if (sublist.classList.contains('collapsed')) {
                sublist.classList.remove('collapsed');
                folderItem.classList.add('open');
                folderItem.parentNode.classList.add('open');
            } else {
                sublist.classList.add('collapsed');
                folderItem.classList.remove('open');
                folderItem.parentNode.classList.remove('open');
            }
        }

        function openFile(filePath) {
            // On mobile, open in new tab
            if (window.innerWidth <= 768) {
                window.open("html/tagview.html?file=" + encodeURIComponent(filePath), "_blank");
            } else {
                // On desktop, load into iframe
                document.getElementById("file-viewer").src = "html/tagview.html?file=" + encodeURIComponent(filePath);
            }
        }

        function searchFiles() {
            const input = document.getElementById('search-box').value.toLowerCase().trim();
            const allFolders = document.querySelectorAll('.folder-container');

            if (input === "") {
                allFolders.forEach(folderContainer => {
                    const folder = folderContainer.querySelector('.file-item.folder');
                    const fileList = folderContainer.querySelector('.file-list');
                    const fileItems = folderContainer.querySelectorAll('.file-item.file');

                    folderContainer.style.display = '';
                    folder.classList.remove('open');
                    folderContainer.classList.remove('open');
                    fileList.classList.add('collapsed');

                    // show all files
                    fileItems.forEach(file => file.style.display = '');
                });
                return;
            }

            allFolders.forEach(folderContainer => {
                const folder = folderContainer.querySelector('.file-item.folder');
                const tagName = folder.querySelector('.file-name').textContent.toLowerCase();
                const fileList = folderContainer.querySelector('.file-list');
                const fileItems = folderContainer.querySelectorAll('.file-item.file');

                let folderMatch = tagName.includes(input);
                let hasMatchingFile = false;

                // Track which files matched
                fileItems.forEach(file => {
                    const fileName = file.querySelector('.file-name').textContent.toLowerCase();
                    if (fileName.includes(input)) {
                        file.style.display = '';
                        hasMatchingFile = true;
                    } else {
                        file.style.display = folderMatch ? '' : 'none';
                    }
                });

                if (folderMatch || hasMatchingFile) {
                    folderContainer.style.display = '';

                    // reset folder state
                    folder.classList.remove('open');
                    folderContainer.classList.remove('open');
                    fileList.classList.add('collapsed');

                    if (hasMatchingFile) {
                        folder.classList.add('open');
                        folderContainer.classList.add('open');
                        fileList.classList.remove('collapsed');
                    }
                } else {
                    folderContainer.style.display = 'none';
                    folder.classList.remove('open');
                    folderContainer.classList.remove('open');
                    fileList.classList.add('collapsed');
                }
            });
        }
    </script>
</body>

</html>
