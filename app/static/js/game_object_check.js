(() => {
    let result;
    if (typeof window.game !== 'undefined' && window.game.players !== undefined) {
        result = { status: 'success', message: 'ゲームオブジェクトが利用可能になりました。' };
    } else if (document.readyState === 'complete') {
        result = { status: 'loading', message: 'ページは読み込まれましたが、ゲームオブジェクトはまだ利用できません。' };
    } else {
        result = { status: 'waiting', message: 'ページの読み込み中です。' };
    }
    return result;
})(); 
