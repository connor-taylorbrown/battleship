(function () {
    var params = {
        prompt: 'Copy link to clipboard',
        alert: 'Copied link to clipboard'
    }

    var tooltip = document.getElementById('tooltip');
    tooltip.innerHTML = params.prompt;

    var share = document.getElementById('share');
    share.onclick = () => {
        var url = window.location.href;
        navigator.clipboard.writeText(url);
        tooltip.innerHTML = params.alert;
    }

    share.onmouseout = () => {
        tooltip.innerHTML = params.prompt;
    }
})();