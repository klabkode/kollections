<!DOCTYPE html>
<html>
  <head>
    <title>KLAB</title>
    <link rel="icon" href="icons/favicon.ico" type="image/x-icon">
    <style>
      body {
        font-family: sans-serif;
        background-color: #eee;
      }
      h1 {
        font-size: 32px;
        margin-left: 5px;
      }
      h2 {
        font-size: 24px;
        margin-left: 5px;
      }
      h3 {
        font-size: 18px;
        margin-top: 5px;
      }
      #header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem;
        background-color: #333;
        color: white;
      }
      #workspace-header {
        font-weight: bold;
        margin-left: 15px;
      }
      #user-info {
        float: right;
        margin-top:   10px;
        margin-right: 10px;
      }
      #user-info img {
        height: 60px;
        border-radius: 50%;
        margin-right: 10px;
      }
      #user-info span {
        font-weight: bold;
      }
      #project-tiles {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
        grid-gap: 1rem;
        margin-left: 15px;
      }
      .project-tile {
        border-radius: 10%;
        background-color: #fff;
        border: 5px solid #eee;
        padding: .5rem;
        text-align: center;
        cursor: pointer;
        font-weight: bold;
        background-color: #cfe2f3;
        /* width: var(--tile-width, 90px); */
        height: var(--tile-height, 90px);
      }
      .project-tile:hover {
        box-shadow: 0 0 5px rgba(0, 0, 0, 0.2);
      }
      .project-tile img {
        max-width: 100%;
        max-height: 100%;
        height: auto;
      }
      #deployment-tiles {
        display: grid;
        grid-gap: .5rem;
        margin-left: 10px;
        grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
      }
      .deployment-tile {
        background-color: #fff;
        border: 5px solid #eee;
        padding: .5rem;
        text-align: center;
        cursor: pointer;
        font-weight: bold;
        /* font-size: 22px; */
        background-color: #cfe2f3;
        /* width: var(--tile-width, 90px); */
        height: var(--tile-height, 30px);
      }
      .deployment-tile:hover {
        box-shadow: 0 0 5px rgba(0, 0, 0, 0.2);
      }
      .deployment-tile img {
        max-width: 100%;
        max-height: 100%;
        height: auto;
      }
      .no-files {
        margin-left: 15px;
        white-space: nowrap;
      }
      .no-files-error {
        color: red;
        margin-left: 15px;
        white-space: nowrap;
      }
      footer {
        padding: 20px 0;
        text-align: center;
      }
    </style>
  </head>
  <body>
    <header id="header">
      <h1>KLAB Dashboard</h1>
     <div id="user-info">
       <img src="icons/avatar/avatar.png" alt="User Avatar">
       <span>Kirubakaran Shanmugam</span>
     </div>
    </header>
    <h2 id="workspace-header">Deployments</h2><hr>
    <?php
      function generate_deployment_tiles($config_file) {
        // Load deployment configs from the file
        $config = file_get_contents($config_file);
        $config = json_decode($config, true);
        if (empty($config)) {
          echo "<p class='no-files-error'>Oops! No web-tools deployed.</p>";
          echo "<p class='no-files'>Please follow these steps to deploy your web-tools:</p>
                <ol>
                  <li>Write the deployed web-tool configs at '<code>/var/www/html/klab/configs</code>'.</li>
                  <li>Refer the pre-defined deployment configs as per your requirements:</li>
                  <ul>
                    <li>For Localhost deployments, see '<code>local-deployments.json</code>'</li>
                    <li>For Docker deployments, see '<code>docker-deployments.json</code>'</li>
                    <li>Name of the deployment configs should be 'deployments.json'</li>
                  </ul>
                  <li>Once the deployment configs are copied, your web-tools will be displayed here.</li>
                </ol>";
        } else {
          echo '<div id="project-tiles">';
          // Generate the tile for each project
          foreach ($config['deployments'] as $deployment) {
            echo '<div class="project-tile" onclick="window.open(\'' . $deployment['url'] . '\', \'_blank\');">';
            echo '<img src="' . $deployment['icon'] . '" alt="' . $deployment['name'] . '" width="60" height="60">';
            echo '<h3>' . $deployment['name'] . '</h3>';
            echo '</div>';
          }
          echo '</div>';
        }
      }

      // Webtools installed in the docker
      echo generate_deployment_tiles('configs/deployments.json');
    ?>
    <br>
    <h2 id="workspace-header">Projects</h2><hr>
    <?php
      function read_projects() {
        $projects = array();
        $dir = "./configs/projects/";
        if (is_dir($dir)) {
          if ($dh = opendir($dir)) {
            while (($file = readdir($dh)) !== false) {
              if (pathinfo($file, PATHINFO_EXTENSION) == "json") {
                $project = json_decode(file_get_contents($dir . $file), true);
                $project['filename'] = $file;
                $projects[] = $project;
              }
            }
            closedir($dh);
          }
        }
        return $projects;
      }

      // Generate project tiles
      function generate_project_tiles($projects) {
        sort($projects);
        if (empty($projects)) {
          echo "<p class='no-files-error'>Oops! No projects deployed. </p>";
          echo "<p class='no-files'>Please follow these steps to deploy your projects:</p>
                <ol>
                  <li>Copy your projects to '<code>/var/klab/projects</code>' directory and</li>
                  <li>Run the '<code>kdeploy</code>' inside the project root directory to deploy it (or)</li>
                  <li>Run the '<code>kdeploy --recursive</code>' at '<code>/var/klab/projects</code>' to deploy the projects recursively</li>
                  <li>Once the deployments completed, your projects will be displayed here.</li>
                </ol>";
        } else {
          echo '<div id="project-tiles">';
          foreach ($projects as $project) {
            echo '<div class="project-tile" onclick="window.open(\'' . $project['url'] . '\', \'_blank\');">';
            echo '<img src="' . $project['icon'] . '" alt="' . $project['name'] . '" width="60" height="60">';
            echo '<h3>' . $project['name'] . '</h3>';
            echo '</div>';
          }
          echo '</div>';
        }
      }

      // Read projects and generate tiles
      $projects = read_projects();
      sort($projects);
      generate_project_tiles($projects);
    ?>

    <br>
    <h2 id="workspace-header">Project based deployments:</h2><hr>
      <?php
        // Function to generate project deployments
        function generate_project_deployments($project) {
          echo '<h2 id="workspace-header">' . $project['name'] . ':</h2>';
          echo '<div id="deployment-tiles">';
          foreach ($project['deployments'] as $deployment) {
            if ($deployment['status']) {
              echo '<div class="deployment-tile" onclick="window.open(\'' . $deployment['url'] . '\', \'_blank\');">';
              echo '<img src="' . $deployment['icon'] . '" alt="icon" width="30" height="30" style="float:left">';
              echo '<div style="margin-top:5px;">' . $deployment['name'] . '</div>';
              echo '</div>';
            }
          }
          echo '</div>';
        }

        foreach ($projects as $project) {
          generate_project_deployments($project);
        }
      ?>
  </body>
  <footer>
    <p>&copy; <?php echo date('Y'); ?> KLAB. All rights reserved.</p>
  </footer>
</html>
