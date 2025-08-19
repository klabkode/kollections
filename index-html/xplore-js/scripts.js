window.onload = function () {
    let breadcrumbPaths = [];
    const FILE_ICON = 'res/file-icon.png';
    const FOLDER_ICON = 'res/folder-icon.png';
    const directoryList = document.querySelector('.directory-list');
    const breadcrumb = document.getElementById('breadcrumb');
    const breadcrumbContainer = document.querySelector('.breadcrumb-container');

    function updateBreadcrumb(path) {
        breadcrumb.innerHTML = '';
        breadcrumbPaths = [];

        const parts = path.split('/').filter(Boolean);
        let currentPath = '';

        const rootLink = document.createElement('a');
        rootLink.textContent = 'Home';
        rootLink.href = '#';
        rootLink.onclick = function (event) {
            event.preventDefault();
            fetchFiles('/'); // Fetch the root directory
        };

        breadcrumb.appendChild(rootLink);
        breadcrumbPaths.push('/');

        parts.forEach((part, index) => {
            currentPath += (index === 0 ? '' : '/') + part;

            const link = document.createElement('a');
            link.textContent = part;
            link.href = '#';
            link.onclick = function (event) {
                event.preventDefault();
                fetchFiles(breadcrumbPaths[index + 1]);
            };

            breadcrumb.appendChild(link);
            breadcrumbPaths.push(currentPath);
        });

        breadcrumbContainer.scrollLeft = breadcrumbContainer.scrollWidth;
    }

    function fetchDiskUsage() {
        fetch('/api/disk-usage')
            .then(response => response.json())
            .then(data => {
                document.getElementById('disk-usage').textContent = `Usage: ${data.used}/${data.size} (${data.usePercentage})`;
            })
            .catch(err => console.error('Error fetching disk usage:', err));
    }

    function fetchFiles(path = '/') {
        fetch(`/api/files?path=${encodeURIComponent(path)}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(files => {
                renderFiles(files);
                updateBreadcrumb(path);

                const dirItemsCount = files.length;
                document.getElementById('dir-nitems').textContent = `${dirItemsCount} items`;

                const currentPath = new URLSearchParams(window.location.search).get('path') || '';
                if (path !== currentPath) {
                    history.pushState({ path }, '', `?path=${encodeURIComponent(path)}`);
                }
            })
            .catch(err => console.error('Error fetching files:', err));
    }

    function renderFiles(files) {
        const fragment = document.createDocumentFragment();
        const directories = files.filter(file => file.isdir);
        const regularFiles = files.filter(file => !file.isdir);

        directoryList.innerHTML = '';

        function createFileItem(file) {
            const fileItem = document.createElement('div');
            fileItem.classList.add('file-item');

            const fileIcon = document.createElement('img');
            fileIcon.src = file.isdir ? FOLDER_ICON : FILE_ICON;
            fileIcon.classList.add('file-icon');
            fileItem.appendChild(fileIcon);

            const fileDetails = document.createElement('div');
            fileDetails.classList.add('file-details');

            const fileName = document.createElement('div');
            fileName.classList.add('file-name');
            fileName.textContent = file.name;
            fileDetails.appendChild(fileName);

            const fileMeta = document.createElement('div');
            fileMeta.classList.add('file-meta');
            fileMeta.textContent = `${file.isdir ? file.nitems + ' items' : file.size} | Modified: ${file.modtime}`;
            fileDetails.appendChild(fileMeta);

            fileItem.appendChild(fileDetails);

            fileItem.onclick = function () {
                if (file.isdir) {
                    fetchFiles(file.path);
                } else {
                    viewFile(file.path);
                }
            };

            return fileItem;
        }

        directories.forEach(directory => {
            const directoryItem = createFileItem(directory);
            fragment.appendChild(directoryItem);
        });

        regularFiles.forEach(file => {
            const fileItem = createFileItem(file);
            fragment.appendChild(fileItem);
        });

        directoryList.appendChild(fragment);
    }

    function viewFile(path) {
        const fileWindow = window.open('fileview.html?path=' + encodeURIComponent(path), '_blank');
        if (!fileWindow) {
            alert('Popup blocked! Please allow popups for this site.');
        }
    }

    window.addEventListener('popstate', (event) => {
        const path = event.state ? event.state.path : '/';
        fetchFiles(path);
    });

    const initialPath = new URLSearchParams(window.location.search).get('path') || '/';
    fetchDiskUsage();
    fetchFiles(initialPath);
};
