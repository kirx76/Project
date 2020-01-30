function activator(url) {
    res = url.split("/");
    if (res[3] === "")
        return "general_link";
    else if (res[3] === "post")
        return "general_link";
    else if (res[3] === "adminpanel")
        return "admin_link";
    else if (res[3] === "addpost")
        return "addpost_link";
    else if (res[3] === "profile")
        return "hprofile_link";
    else if (res[3] === "login")
        return "authorization_link";
    else if (res[3] === "register")
        return "registration_link";
}

function decodeHTMLEntities(text) {
    var entities = [
        ['amp', '&'],
        ['\r\n', ' '],
        ['apos', '\''],
        ['#x27', '\''],
        ['#x2F', '/'],
        ['#39', '\''],
        ['#47', '/'],
        ['lt', '<'],
        ['gt', '>'],
        ['nbsp', ' '],
        ['quot', '"']
    ];

    for (var i = 0, max = entities.length; i < max; ++i)
        text = text.replace(new RegExp('&' + entities[i][0] + ';', 'g'), entities[i][1]);

    return text;
}

function tag_parser(base_tag) {
    let array_of_tags = base_tag.split(",");
    console.log(base_tag);
    console.log(array_of_tags);
    let return_text = '';
    for (index = 0; index < array_of_tags.length; ++index) {
        return_text += array_of_tags[index];
    }
    console.log(return_text);
    return return_text
}