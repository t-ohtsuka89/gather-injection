const createTeleportButtons = () => {
    const teleportButton = (text, x, y) => {
        const btn = document.createElement('button');
        btn.innerHTML = text;
        btn.style = `border: none; outline: none; font: inherit; color: inherit; background-color: rgb(255 0 0 / 0.8); color: #fff; padding: 5px 12px;`;
        btn.onclick = () => {
            const mapId = game.getMyPlayer().map;
            game.teleport(mapId, x, y);
        };
        return btn;
    };

    const e = document.createElement('div');
    e.style = `position: fixed; top: 60px; left: 30px; z-index: 1000;`;

    e.appendChild(teleportButton('sample_button1', 1, 1));
    e.appendChild(teleportButton('sample_button2', 10, 10));
    e.appendChild(teleportButton('sample_button3', 20, 20));

    return e;
};

const waitForDocumentReady = () => {
    return new Promise((resolve) => {
        if (document.readyState === 'complete') {
            resolve();
        } else {
            document.addEventListener('readystatechange', () => {
                if (document.readyState === 'complete') {
                    resolve();
                }
            });
        }
    });
};

const initTeleportButtons = async () => {
    await waitForDocumentReady();
    const buttons = createTeleportButtons();
    const root = document.getElementById('root');
    if (root) {
        root.appendChild(buttons);
        console.log('テレポートボタンがルート要素に追加されました');
    } else {
        console.error('ルート要素が見つかりません');
    }
};

initTeleportButtons();
