(() => {
'use strict';


// source https://dev.to/ycmjason/building-a-simple-virtual-dom-from-scratch-3d05
const createElement = (tagName, { attrs = {}, children = [] }) => {
    const vElem = Object.create(null);

    Object.assign(vElem, {
        tagName,
        attrs,
        children,
    });

    return vElem;
};

const renderElem = ({ tagName, attrs, children}) => {
    const $el = document.createElement(tagName);

    for (const [k, v] of Object.entries(attrs)) {
        $el.setAttribute(k, v);
    }

    for (const child of children) {
        if (typeof child === 'string') {
            $el.innerHTML = child;
        } else {
            $el.appendChild(renderElem(child));
        }
    }

    return $el;
};

const attachEvents = ($node) => {
    if ($node.children[2].children.length <= 2) {
        return true;
    }
    const $link = $node.children[2].children[2].children[0];
    if ($link.attributes['class'].value !== 'toggle-media') {
        return true;
    }

    // first is the link then the medias
    const $imgs = Array.from($node.children[2].children[2].children).slice(1);
    $link.addEventListener('click', (event) => {
        event.preventDefault();
        $imgs.forEach( $img => {
            if ($img.style.display === 'none') {
                $img.style.display = "block";
                $link.text = "Hide media";
            } else {
                $img.style.display = "none";
                $link.text = "Show media";
            }
        });
    });
};

const patch = ($node, $target) => {
    const nodeDate = $node.attributes['data-date'].value;
    let inserted = false;
    for (var child of $target.childNodes.entries()) {
        if (!child[1].attributes) {
            continue;
        }
        const childDate = child[1].attributes['data-date'].value;
        if (!childDate) {
            continue;
        }
        if (nodeDate > childDate) {
            $target.insertBefore($node, child[1]);
            inserted = true;
            break;
        }
    }
    if (!inserted) {
        $target.appendChild($node);
    }
};

const computevArticle = (activity) => {
    const vArticle = createElement('article', {
        attrs: {
            id: activity['sid'],
            'data-date': activity['timestamp']
        },
        children: [
            createElement('header', {
                children: [
                    createElement('img', {
                        attrs: {
                            src: activity['r_author_avatar'],
                            class: "avatar"
                        }
                    }),
                    createElement('strong', {
                        children: [
                            createElement('a', {
                                attrs: {
                                    href: activity['r_author_url'],
                                    rel: 'nofollow noopener',
                                    target: '_blank',
                                    title: activity['r_author_title']
                                },
                                children: [
                                    activity['r_author']
                                ]
                            })
                        ]
                    })
                ]
            }),
            createElement('div', {
                attrs: {
                    class: 'content'
                },
                children: [
                    activity['r_content']
                ]
            }),
            createElement('footer', {
                children: [
                    createElement('div', {
                        attrs: {class: 'counters'},
                        children: [
                            activity['reblog_count'] + ' ♺ ' + activity['favorite_count'] + ' ☆',
                        ]
                    }),
                    createElement('div', {
                        children: [
                            'On ' + activity['extractor'] + ' ',
                            createElement('a', {
                                attrs: {
                                    href: activity['url'],
                                    rel: 'nofollow noopener',
                                    target: '_blank'
                                },
                                children: [
                                    activity['date']
                                ]
                            })
                        ]
                    })
                ]
            })
        ]
    });
    if (activity['is_r']) {
        vArticle.children[0].children[1].children.push(
            createElement('span', {
                attrs: {
                    class: 'activity_info'
                },
                children: [
                    " ♺ by ",
                    createElement('a', {
                        attrs: {
                            href: activity['author_url'],
                            rel: 'nofollow noopener',
                            target: '_blank'
                        },
                        children: [activity['author']]
                    })
                ]
            })
        );
    }

    if (activity['medias'].length) {
        vArticle.children[2].children.push(
            createElement('div', {
                children: [
                    createElement('a', {
                        attrs: {
                            href: '#',
                            class: 'toggle-media',
                        },
                        children: ["Show medias"]
                    })
                ]
            })
        );
        activity['medias'].forEach( media => {
            const $mediaLink = createElement('a', {
                attrs: {
                    style: 'display:none;',
                    href: media['url'],
                    rel: 'nofollow noopener',
                    target: '_blank'
                },
                children: []
            });
            if (media['type'] == 'image') {
                $mediaLink.children.push(
                    createElement('img', {
                        attrs: {
                            src: media['inline']
                        }
                    })
                );
            } else if (media['type'] == 'video') {
                $mediaLink.children.push(
                    createElement('video', {
                        attrs: {
                            src: media['inline'],
                            controls: ''
                        }
                    })
                );
            }
            vArticle.children[2].children[2].children.push($mediaLink);
        });
    }

    return vArticle;
};

const computevFirstBorder = (activity) => {
    return createElement('article', {
        attrs: {
            id: "first-" + activity.extractor,
            'data-date': activity.timestamp + 1,
            style: "display:none",
        },
        children: [
            createElement('a', {
                attrs: {
                    href: '#',
                    title: "Load more recent activities on " + activity.extractor
                },
                children: [
                    "⌃ " + activity.extractor
                ]
            })
        ]
    });
};

const computevLastBorder = (activity) => {
    return createElement('article', {
        attrs: {
            id: "last-" + activity.extractor,
            'data-date': activity.timestamp - 1,
            // style: "display:none",
        },
        children: [
            createElement('a', {
                attrs: {
                    href: '#',
                    title: "Load older activities on " + activity.extractor
                },
                children: [
                    "⌄ " + activity.extractor
                ]
            })
        ]
    });
};


let upGaps = {};
let downGaps = {};

const renderBorders = ($articleList) => {
    for (let extractor in upGaps) {
        const vFirst = computevFirstBorder(upGaps[extractor]);
        const $first = renderElem(vFirst);
        let $activityDom = document.getElementById("first-"+extractor);
        if (!$activityDom || $activityDom.id !== $first.id) {
            if ($activityDom)
                $activityDom.remove();
            patch($first, $articleList);
        }

        const vLast = computevLastBorder(downGaps[extractor]);
        const $last = renderElem(vLast);
        $activityDom = document.getElementById("last-"+extractor);
        if (!$activityDom || $activityDom.id !== $last.id) {
            if ($activityDom)
                $activityDom.remove();
            patch($last, $articleList);
        }
    }

};

const _isMoreRecent = (first, second) => {
    return first.date > second.date;
};

const _isSame = (first, second) => {
    return first.sid === second.sid;
};

const fetchPreviousActivities = async (count) => {
    let minStatus = false;
    for (const extractor in downGaps) {
        // fetch only the most out of date first
        if (!minStatus || _isMoreRecent(downGaps[extractor], minStatus)) {
            minStatus = downGaps[extractor];
        }
    }

    const minId = downGaps[minStatus.extractor].sid;
    const resp = await fetch(`/fetch-previous/${minStatus.extractor}/${count}/${minId}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    });
    const activities = await resp.json();
    processFetchedActivities(activities);
    // update the minStatus with the new fetched minimum
    minStatus = downGaps[minStatus.extractor];

    for (const extractor in downGaps) {
        if (minStatus.extractor === extractor) {
            continue;
        }

        if (_isMoreRecent(minStatus, downGaps[extractor])) {
            // `minStatus.extractor` still did not catched up with `extractor`
            continue;
        }

        const minId = downGaps[extractor].sid;
        fetch(`/fetch-previous/${extractor}/${count}/${minId}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        }).then((resp) => {
            return resp.json();
        }).then((activities) => {
            processFetchedActivities(activities);
        });
    }
};

const fetchActivities = async (count) => {

    const resp = await fetch('/fetch/' + count, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    });

    return processFetchedActivities(await resp.json());
};

const processFetchedActivities = (activities) => {
    const $articleList = document.getElementById('article-list');
    let maxActivities = {};
    let minActivities = {};

    activities.forEach(activity => {
        const extr = activity.extractor;

        if (!(extr in maxActivities) || _isMoreRecent(activity, maxActivities[extr])) {
            // initialise border activities
            maxActivities[extr] = activity;
        }
        if (!(extr in minActivities) || _isMoreRecent(minActivities[extr], activity)) {
            // initialise border activities
            minActivities[extr] = activity;
        }

        const $activityDom = document.getElementById(activity['sid']);
        if (!$activityDom) {

            const vArticle = computevArticle(activity);
            const $article = renderElem(vArticle);
            attachEvents($article);
            patch($article, $articleList);

        }
    });
    for (const extractor in maxActivities) {
        if (!(extractor in upGaps) || _isMoreRecent(maxActivities[extractor], upGaps[extractor])) {
            upGaps[extractor] = maxActivities[extractor];
        }
    }
    for (const extractor in minActivities) {
        if (!(extractor in downGaps) || _isMoreRecent(downGaps[extractor], minActivities[extractor])) {
            downGaps[extractor] = minActivities[extractor];
        }
    }
    renderBorders($articleList);

};

document.addEventListener("DOMContentLoaded", function() {

    const $refreshButton = document.getElementById('refresh-button');
    $refreshButton.addEventListener('click', (event) => {
        event.preventDefault();
        fetchActivities(30);
    });
    document.addEventListener('keydown', (event) => {
        const keyName = event.key;
        if (keyName == 'Home') {
            fetchActivities(30);
        } else if (keyName == 'End') {
            fetchPreviousActivities(30);
        }
    });
    fetchActivities(20);


});

})();
