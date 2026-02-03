
// Tutorial Logic using driver.js

window.initTutorial = function () {
    // Check if driver is loaded
    if (!window.driver || !window.driver.js) {
        console.error('Driver.js is not loaded');
        return null;
    }

    const driver = window.driver.js.driver;

    const driverObj = driver({
        showProgress: true,
        allowClose: true,
        // Customize text for Japanese users
        nextBtnText: '次へ',
        prevBtnText: '戻る',
        doneBtnText: '完了',
        progressText: '{{current}} / {{total}}',
        steps: [
            {
                element: '.header-overlay',
                popover: {
                    title: 'SEISMIC WORLDへようこそ',
                    description: '世界の地震活動を可視化するインタラクティブマップです。<br>このガイドでは主な機能を紹介します。'
                }
            },
            {
                element: '#map',
                popover: {
                    title: 'マップ表示エリア',
                    description: '世界中で発生した地震が円として描画されます。<br>・<span style="color:#00a8cc">青</span>: M4.5-5 (中規模)<br>・<span style="color:#ff9900">黄</span>: M5-6 (強震)<br>・<span style="color:#e51c23">赤</span>: M6+ (大地震)'
                }
            },
            {
                element: '.year-tabs-overlay',
                popover: {
                    title: 'データの切り替え',
                    description: '「直近1年」や過去の年代（2011年〜）を選択してデータを切り替えます。<br>データ量が多い年代は読み込みに時間がかかる場合があります。'
                }
            },
            {
                element: '.controls-overlay',
                popover: {
                    title: '再生コントロール',
                    description: '再生ボタン▶で時系列アニメーションを開始します。<br>スライダーを動かすことで、任意の時点にジャンプできます。'
                }
            },
            {
                element: '.stats-container',
                popover: {
                    title: '統計データ',
                    description: '表示中の期間内の地震総数と、最大マグニチュードが表示されます。'
                }
            },

            {
                element: '#tutorial-toggle',
                popover: {
                    title: 'いつでも確認できます',
                    description: '使い方が分からなくなったら、このボタンを押して再度ガイドを見ることができます。'
                }
            }
        ]
    });

    return driverObj;
};

window.startTutorial = function () {
    const driverObj = window.initTutorial();
    if (driverObj) {
        driverObj.drive();
    }
};

window.checkFirstVisit = function () {
    const hasSeenTutorial = localStorage.getItem('seismic_tutorial_seen');
    if (!hasSeenTutorial) {
        // Delay slightly to ensure map is loaded
        setTimeout(() => {
            window.startTutorial();
            localStorage.setItem('seismic_tutorial_seen', 'true');
        }, 1500);
    }
};
