'use strict';

document.addEventListener("DOMContentLoaded",function(){

    const response = fetch('/home', {
        method: 'GET',
        headers:{
          'Content-Type': 'application/json'
        }
    }).then(function(json) {
        console.log(json);
    });


});
