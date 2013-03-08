<?xml version="1.0" encoding="UTF-8" ?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    
    <xsl:template match="view[@type = 'quest-check']">
        <xsl:variable name="questId"><xsl:value-of select="param[@name = 'questId']/@value" /></xsl:variable>
        <xsl:variable name="questName"><xsl:value-of select="param[@name = 'questName']" /></xsl:variable>
        <div class="page-header"><a href="login"><img src="static/images/quest.png" /></a></div>
        <div class="page-inform">
            <p class="trail"><a href="quest/view">to quests</a></p>
            <p class="header"><xsl:value-of select="$questName" /> </p>
            <xsl:apply-templates select="verdict" />
        </div>
    </xsl:template>

    <xsl:template match="verdict[@status = 'accepted']">
        <p>Congratulations, you solved the quest!</p>
        <p><xsl:value-of select="." /></p>
    </xsl:template>
    
    <xsl:template match="verdict[@status = 'postponed']">
        <p>Your solution was accepted and soon will be checked by jury</p>
        <xsl:value-of select="." />
    </xsl:template>

    <xsl:template match="verdict[@status = 'rejected']">
        <p>Wrong solution: <a href="quest/get?questId={../param[@name = 'questId']/@value}">try</a> again</p>
        <xsl:value-of select="." />
    </xsl:template>
</xsl:stylesheet>
