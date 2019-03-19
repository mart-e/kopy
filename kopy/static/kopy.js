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

const mount = ($node, $target) => {
    $target.appendChild($node);
    return $node;
};


document.addEventListener("DOMContentLoaded", function() {

    fetch('/fetch/20', {
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
                            'data-date': status['date']
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
                                    `On {status['extractor']} `,
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
                    });

                    if (status['is_r']) {
                        vArticle.children[0].children[1].children.push(
                            createElement('span', {
                                attrs: {
                                    class: 'status_info'
                                },
                                children: [
                                    "♺ by ",
                                    createElement('a', {
                                        attrs: {
                                            href: status['author_url']
                                        },
                                        children: [
                                            status['author']
                                        ]
                                    })
                                ]
                            })
                        );
                    }
                    const $article = render(vArticle);
                    mount($article, $articleList);
                }
            });
        });
    });

});

})();