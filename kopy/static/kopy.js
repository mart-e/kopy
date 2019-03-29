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
            $el.appendChild(render(child));
        }
    }

    return $el;
};

const render = (vNode) => {
    // if (typeof vNode === 'string') {
    //     return document.createTextNode(vNode);
    // }

    // we assume everything else to be a virtual element
    return renderElem(vNode);
};

const attachEvents = ($node) => {
    if ($node.children[2].children.length <= 2) {
        return true;
    }
    const $link = $node.children[2].children[2].children[0];
    if ($link.attributes['class'].value !== 'toggle-media') {
        return true;
    }

    const $img = $node.children[2].children[2].children[1];
    $link.addEventListener('click', (event) => {
        event.preventDefault();
        if ($img.style.display === 'none') {
            $img.style.display = "block";
            $link.text = "Hide media";
        } else {
            $img.style.display = "none";
            $link.text = "Show media";
        }
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

const fetchStatuses = (count) => {

    fetch('/fetch/' + count, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(function (resp) {
        const $articleList = document.getElementById('article-list');
        resp.json().then(statuses => {
            statuses.forEach(status => {
                const $statusDom = document.getElementById(status['sid']);
                if (!$statusDom) {
                    const vArticle = createElement('article', {
                        attrs: {
                            id: status['sid'],
                            'data-date': status['timestamp']
                        },
                        children: [
                            createElement('header', {
                                children: [
                                    createElement('img', {
                                        attrs: {
                                            src: status['r_author_avatar'],
                                            class: "avatar"
                                        }
                                    }),
                                    createElement('strong', {
                                        children: [
                                            createElement('a', {
                                                attrs: {
                                                    href: status['r_author_url'],
                                                    rel: 'nofollow noopener',
                                                    target: '_blank'
                                                },
                                                children: [
                                                    status['r_author']
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
                                    status['r_content']
                                ]
                            }),
                            createElement('footer', {
                                children: [
                                    createElement('div', {
                                        attrs: {class: 'counters'},
                                        children: [
                                            status['reblog_count'] + ' ♺ ' + status['favorite_count'] + ' ☆',
                                        ]
                                    }),
                                    createElement('div', {
                                        children: [
                                            'On ' + status['extractor'] + ' ',
                                            createElement('a', {
                                                attrs: {
                                                    href: status['url'],
                                                    rel: 'nofollow noopener',
                                                    target: '_blank'
                                                },
                                                children: [
                                                    status['date']
                                                ]
                                            })
                                        ]
                                    })
                                ]
                            })
                        ]
                    });

                    if (status['is_r']) {
                        vArticle.children[0].children[1].children.push(
                            createElement('span', {
                                attrs: {
                                    class: 'status_info'
                                },
                                children: [
                                    " ♺ by ",
                                    createElement('a', {
                                        attrs: {
                                            href: status['author_url'],
                                            rel: 'nofollow noopener',
                                            target: '_blank'
                                        },
                                        children: [status['author']]
                                    })
                                ]
                            })
                        );
                    }

                    if (status['medias'].length) {
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
                        status['medias'].forEach( media => {
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
                    const $article = render(vArticle);
                    attachEvents($article);
                    patch($article, $articleList);
                }
            });
        });
    });
};

document.addEventListener("DOMContentLoaded", function() {

    const $refreshButton = document.getElementById('refresh-button');
    $refreshButton.addEventListener('click', (event) => {
        event.preventDefault();
        fetchStatuses(30);
    });
    document.addEventListener('keydown', (event) => {
        const keyName = event.key;
        if (keyName == 'Home') {
            fetchStatuses(30);
        }
    });
    fetchStatuses(20);


});

})();