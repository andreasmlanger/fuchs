function calculateSimilarity(s1, s2) {
    s1 = deAccent(s1);
    s2 = deAccent(s2);
    var longer = s1;
    var shorter = s2;
    if (s1.length < s2.length) {
        longer = s2;
        shorter = s1;
    }
    var longerLength = longer.length;
    if (longerLength == 0) {
        return 1.0;
    }
    return (longerLength - editDistance(longer, shorter)) / parseFloat(longerLength);
}

function editDistance(s1, s2) {
    s1 = s1.toLowerCase();
    s2 = s2.toLowerCase();
    var costs = new Array();
    for (var i = 0; i <= s1.length; i++) {
        var lastValue = i;
        for (var j = 0; j <= s2.length; j++) {
            if (i == 0) {
                costs[j] = j;
            } else {
                if (j > 0) {
                    var newValue = costs[j - 1];
                    if (s1.charAt(i - 1) != s2.charAt(j - 1)) {
                        newValue = Math.min(Math.min(newValue, lastValue), costs[j]) + 1;
                    }
                    costs[j - 1] = lastValue;
                    lastValue = newValue;
                }
            }
        }
        if (i > 0)
            costs[s2.length] = lastValue;
        }
    return costs[s2.length];
}

function changeLanguage(lang) {
    var activeFlag = document.getElementById('flag-' + lang);
    foreignLanguage = activeFlag.getAttribute('data-language');
    Array.from(document.getElementsByClassName("flag")).forEach((flag) => {
        flag.style.filter = (flag == activeFlag) ? "grayscale(0%)" : "grayscale(90%)";
    });
    updatePage();
    // only on 'New Vocabulary' page:
    var input = document.getElementById('word-1');
    if (input) {
        input.value = '';
        if (lang == 'jp') {
            toggleHiraganaInput(input, true)
        } else {
            toggleHiraganaInput(input, false)
        }
        document.getElementById('word-2').value = '';
    }
}

function toggleHiraganaInput(input, enable) {
    // Documentation: https://wanakana.com/
    if (enable) {
        wanakana.bind(input);
    } else {
        try {
            wanakana.unbind(input);
        } catch (error) {
        }
    }
}

function getLanguageName() {
    switch (foreignLanguage) {
        case 'en':
            return "English";
        case 'fr':
            return "French";
        case 'es':
            return "Spanish";
        case 'pt':
            return "Portuguese";
        case 'jp':
            return "Japanese";
        case 'de':
            return "German";
    }
}

function deAccent(string) {
    return string.normalize('NFD').replace(/\p{Diacritic}/gu, "")
}

const randomItem = arr => arr.splice((Math.random() * arr.length) | 0, 1);
