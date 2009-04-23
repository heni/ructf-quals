<?xml version="1.0" encoding="UTF-8" ?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    
    <xsl:template match="view[@type = 'jury-quest-get']">
        <xsl:variable name="questId"><xsl:value-of select="param[@name = 'questId']/@value" /></xsl:variable>
        <xsl:variable name="questName"><xsl:value-of select="param[@name = 'questName']" /></xsl:variable>
        <div class="page-header"><a href="login"><img src="static/images/quest.png" /></a></div>
        <div class="page-inform">
            <p class="trail"><a href="quest">вернуться</a></p>
            <p class="header"><xsl:value-of select="$questName" /></p>
            <xsl:apply-templates select="quest/view" />
            <p class="small-header"> 
                Решение от <span class="team-select"><xsl:value-of select="solution/@team" /></span>
            </p>
            <span class="time">(<xsl:value-of select="solution/@time" />)
                <xsl:choose>
                    <xsl:when test="solution/@status = 'accepted'"> решение принято </xsl:when>
                    <xsl:when test="solution/@status = 'rejected'"> решение отвергнуто </xsl:when>
                    <xsl:when test="solution/@status = 'postponed'"> решение отложено </xsl:when>
                </xsl:choose>
                [<xsl:value-of select="solution/verdict/text()" />]
            </span>
            <p style="margin: 0.5em 0 0.5em 2em"><xsl:value-of select="solution/text()" /></p>
            <xsl:if test="solution/@file">
                <a href="{solution/@file}">Материалы от команды</a>
            </xsl:if>
            <div id="btn-panel">
                <input type="button" class="button" value="Принять" onclick="showPostForm('quest/accept');" />
                <input type="button" class="button" value="Отвергнуть" onclick="showPostForm('quest/reject');" />
            </div>
            <form action="" id="post-form" name="post-form" method="POST" >
                <input type="hidden" name="questId" value="{$questId}"/>
                <input type="hidden" name="solution" value="{solution/@id}"/>
                <label>Введите комментарий:</label>
                <input style="margin: 5px" type="text" name="actionString" size="50"/>
                <input type="submit" value="Отправить" />
            </form> 
        </div>
    </xsl:template>
</xsl:stylesheet>
