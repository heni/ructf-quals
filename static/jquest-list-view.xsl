<?xml version="1.0" encoding="UTF-8" ?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    
    <xsl:template match="view[@type = 'jury-quest-list']">
        <xsl:variable name="questId"><xsl:value-of select="param[@name = 'questId']/@value" /></xsl:variable>
        <xsl:variable name="questName"><xsl:value-of select="param[@name = 'questName']" /></xsl:variable>
        <xsl:variable name="ppndMode"><xsl:value-of select="@postponed"/></xsl:variable>
        <div class="page-header"><a href="login"><img src="static/images/quest.png" /></a></div>
        <div class="page-inform">
            <p class="trail"><a href="quest">вернуться</a></p>
            <p class="header"><xsl:value-of select="$questName" /> 
                <xsl:if test="$ppndMode = 'true'">&#160;(непроверенные решения)</xsl:if>
                <xsl:if test="not($ppndMode = 'true')">&#160;(решения)</xsl:if>
            </p>
            <ul>
                <xsl:for-each select="solution">
                    <li>
                        <span class="team-select link" onclick="showQuest('{$questId}', '{@id}');"><xsl:value-of select="@team" /></span>
                        &#160;<span class="time">(<xsl:value-of select="@time" />)
                        <xsl:if test="not($ppndMode = 'true')">
                            <xsl:choose>
                                <xsl:when test="@status = 'accepted'"> решение принято </xsl:when>
                                <xsl:when test="@status = 'rejected'"> решение отвергнуто </xsl:when>
                                <xsl:when test="@status = 'postponed'"> решение отложено </xsl:when>
                            </xsl:choose>
                        </xsl:if></span>
                    </li>
                </xsl:for-each>
            </ul>
        </div>
        <form style="display:none" action="quest/get" id="post-form" name="post-form" method="POST">
            <input type="hidden" name="questId" />
            <input type="hidden" name="solution" />
        </form>
    </xsl:template>
</xsl:stylesheet>
