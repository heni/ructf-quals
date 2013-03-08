<?xml version="1.0" encoding="UTF-8" ?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    
    <xsl:template match="view[@type = 'quest']">
        <xsl:variable name="questId"><xsl:value-of select="param[@name = 'questId']/@value" /></xsl:variable>
        <xsl:variable name="questName"><xsl:value-of select="param[@name = 'questName']" /></xsl:variable>
        <div class="page-header"><a href="login"><img src="static/images/quest.png" /></a></div>
        <div class="page-inform">
            <p class="trail"><a href="quest/view">to quests</a></p>
            <p class="header"><xsl:value-of select="$questName" /> </p>
            <xsl:apply-templates select="quest/view" />
            <form style="margin-top: 2em" method="post" action="quest/check">
                <label style="margin: 5px">Answer</label>
                <input type="hidden" name="questId" value="{$questId}" />
                <input style="margin: 5px" class="text" name="actionString" size="50"/>
                <input style="margin: 5px" class="button" type="submit" value="Ответить" />
            </form>
        </div>
    </xsl:template>

    <xsl:template match="view[@mode = 'html']">
        <xsl:copy-of select="." />
    </xsl:template>
    
    <xsl:template match="view[@mode = 'text']">
        <xsl:value-of select="." />
    </xsl:template>

    <xsl:template match="view[@mode = 'attachment']">
        <p><a href="{@src}">additional material</a></p>
    </xsl:template>
</xsl:stylesheet>
