function customQuestAction(path, questId)
{
    var frm = document.forms["post-form"];
    frm.action = path;
    frm.questId.value = questId;
    frm.submit();
}
function openQuest(questId)  { customQuestAction("quest/open", questId); }
function closeQuest(questId) { customQuestAction("quest/close", questId); }
function getAllSolutions(questId) { customQuestAction("quest/all", questId); }
function getUncheckedSolutions(questId) { customQuestAction("quest/get", questId); }


function customAction(path, attrs)
{ 
    var frm = document.forms["post-form"];
    frm.action = path;
    for( key in attrs ) {
        if (attrs[key] != undefined && frm[key] != undefined) 
            frm[key].value = attrs[key];
    }
    frm.submit();
}
function deleteNewsItem(eventId) { customAction("news/delete", {'event': eventId}); }
function navigateNews(page)      { customAction("news", {'page': page}); }

function showQuest(questId, solution)
{
    var frm = document.forms["post-form"];
    frm.action="quest/get";
    frm.questId.value = questId; 
    if (solution != undefined)
        frm.solution.value = solution;
    frm.submit(); 
}

function showPostForm(action)
{
    var frm = document.forms["post-form"];
    var pnl = document.getElementById("btn-panel");
    frm.setAttribute("action", action);
    frm.style.display = "block";
    pnl.style.display = "none";
}

function setcookie(name, value, expires, path, domain, secure)
{
    expires instanceof Date ? expires = expires.toGMTString() : typeof(expires) == 'number' && (expires = (new Date(+(new Date) + expires * 1e3)).toGMTString());
    var r = [name + "=" + escape(value)], s, i;
    for(i in s = {expires: expires, path: path, domain: domain}){
        s[i] && r.push(i + "=" + s[i]);
    }
    return secure && r.push("secure"), document.cookie = r.join(";"), true;
}


function changeLanguage(lang)
{
   setcookie("lang", lang); 
}
