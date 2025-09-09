function $(target) {
    if (typeof target === "string") {
        return document.querySelector(target);
    }
    return target;
}

function $$(target) {
    if (typeof target === "string") {
        return document.querySelectorAll(target);
    }
    if (target.forEach) {
        return target;
    }
    return [target];
}

function scrollTo(target) {
    const container = $(target).closest(".container");
    container.scrollTop = $(target).offsetTop - 20;
}

function hide(target) {
    $$(target).forEach(function(element) {
        element.style.display = "none";
    });
}

function show(target) {
    $$(target).forEach(function(element) {
        element.style.display = "block";
    });
}

function isVisible(target) {
    return $(target).style.display === "block";
}

function activate(target) {
    $$(target).forEach(function(element) {
        element.classList.add("active");
    });
}

function deactivate(target) {
    $$(target).forEach(function(element) {
        element.classList.remove("active");
    });
}

function getLink(target) {
    return $(target).getAttribute("href").substring(1);
}

function openToc() {
    show("#toc");
    activate("#open-toc");
    scrollTo("nav#toc a.active");
}

function closeToc() {
    hide("#toc");
    deactivate("#open-toc");
}

function toggleToc() {
    if (isVisible("#toc")) {
        closeToc();
    } else {
        openToc();
    }
}

function getFragment() {
    const fragment = window.location.hash.substring(1);
    if (fragment) {
        return fragment;
    }
    return getLink("nav#toc ul.chapters a");
}

function selectChapter() {
    const fragment = getFragment();
    hide("section.chapter");
    deactivate("nav#toc a");
    let targetSection = document.getElementById(fragment);
    let targetLink = document.querySelector(`nav#toc a[href="#${fragment}"]`);
    if (!targetSection || !targetLink) {
        return;
    }
    if (targetSection.tagName === "H2") {
        targetSection = targetSection.closest("section.chapter");
    }
    if (targetSection.classList.contains("chapter")) {
        show(targetSection);
    }
    activate(targetLink);
    const sectionsList = targetLink.closest("ul.sections");
    if (sectionsList) {
        const chapterLink = sectionsList.closest("li").querySelector("a");
        activate(chapterLink);
    }
    scrollTo(`#${fragment}`);
}

document.addEventListener("DOMContentLoaded", function() {
    selectChapter();
    document.getElementById("open-toc").addEventListener("click", toggleToc);
});

window.addEventListener("hashchange", function() {
    closeToc();
    selectChapter();
    //scrollTo(`#${getFragment()}`);
});
