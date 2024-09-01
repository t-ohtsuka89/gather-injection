// wait_for_game_object.js
(function waitForGameObject() {
    return new Promise((resolve) => {
        const checkInterval = 500; // 500ミリ秒ごとにチェック
        const maxWaitTime = 30000; // 最大30秒待機
        let elapsedTime = 0;

        const intervalId = setInterval(() => {
            if (typeof window.game !== 'undefined' && window.game.players !== undefined) {
                clearInterval(intervalId);
                resolve({ status: 'success', message: 'ゲームオブジェクトが利用可能になりました。' });
            } else {
                elapsedTime += checkInterval;
                if (elapsedTime >= maxWaitTime) {
                    clearInterval(intervalId);
                    resolve({ status: 'timeout', message: 'ゲームオブジェクトの待機がタイムアウトしました。' });
                }
            }
        }, checkInterval);
    });
})();
