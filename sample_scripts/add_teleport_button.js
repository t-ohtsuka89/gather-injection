const createTeleportButtons = () => {
    const teleportButton = (text, x, y) => {
        const btn = document.createElement('button');
        btn.innerHTML = text;
        btn.style = `border: none; outline: none; font: inherit; color: inherit; background-color: rgb(255 0 0 / 0.8); color: #fff; padding: 5px 12px;`;
        btn.onclick = (() => {
            const mapId = window.game.getMyPlayer().map;
            window.game.teleport(mapId, x, y);
        });
        return btn;
    };

    const e = document.createElement('div');
    e.style = `position: fixed; top: 60px; left: 30px; z-index: 1000;`;

    e.appendChild(teleportButton('sample_button1', 1, 1));
    e.appendChild(teleportButton('sample_button2', 10, 10));
    e.appendChild(teleportButton('sample_button3', 20, 20));

    return e;
};

const waitForGather = (maxAttempts = 60, interval = 1000) => {
    let attempts = 0;
    const checkAndCreate = () => {
        if (window.game && window.game.getMyPlayer) {
            console.log('Gather game object found, creating teleport buttons');
            const buttons = createTeleportButtons();
            const insertButtons = () => {
                const root = document.getElementById('root');
                if (root) {
                    root.appendChild(buttons);
                    console.log('Teleport buttons added to the root element');
                } else {
                    console.log('Root element not found, retrying...');
                    setTimeout(insertButtons, 1000);
                }
            };
            insertButtons();
        } else if (attempts < maxAttempts) {
            console.log(`Waiting for Gather game object... (Attempt ${attempts + 1}/${maxAttempts})`);
            attempts++;
            setTimeout(checkAndCreate, interval);
        } else {
            console.error('Failed to find Gather game object after maximum attempts');
        }
    };
    checkAndCreate();
};

const initScript = () => {
    console.log('Teleport script initialized');
    if (document.readyState === 'complete') {
        waitForGather();
    } else {
        window.addEventListener('load', waitForGather);
    }
};

initScript();
