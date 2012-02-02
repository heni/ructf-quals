<?xml version="1.0" encoding="UTF-8" ?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    
    <xsl:template match="view[@type = 'jury-quest-list']">
        <form style="display:none" id="post-form" name="post-form" method="POST">
            <input type="hidden" name="questId" />
            <input type="hidden" name="solution" />
        </form>
        <xsl:variable name="questId"><xsl:value-of select="quest/@id" /></xsl:variable>
        <xsl:variable name="questName"><xsl:value-of select="quest/name" /></xsl:variable>
        <xsl:variable name="needOpen"><xsl:value-of select="quest/param[@name = 'quest4open']/@value" /></xsl:variable>
        <xsl:variable name="needClose"><xsl:value-of select="quest/param[@name = 'quest4close']/@value" /></xsl:variable>
        <xsl:variable name="ppndMode"><xsl:value-of select="@postponed"/></xsl:variable>
        <div class="page-header"><a href="login"><img src="static/images/quest.png" /></a></div>
        <div class="page-inform">
            <p class="trail">
                <xsl:if test="$needOpen = 'true'">
                    <span class="link" onclick="openQuest('{$questId}');">открыть квест</span>
                </xsl:if>
                <xsl:if test="$needClose = 'true'">
                    <span class="link" onclick="closeQuest('{$questId}');">закрыть квест</span>
                </xsl:if>
                <xsl:if test="$ppndMode = 'true'">
                    <span class="link" onclick="getAllSolutions('{$questId}');">все решения</span>
                    <span class="select-link">непроверенные</span>
                </xsl:if>
                <xsl:if test="$ppndMode != 'true'">
                    <span class="select-link">все решения</span>
                    <span class="link" onclick="getUncheckedSolutions('{$questId}');">непроверенные</span>
                </xsl:if>
                <a href="quest">вернуться</a>
            </p>
            <p class="header">
                <xsl:value-of select="$questName" /> (<xsl:value-of select="$questId" />) 
            </p>
            <table class="jlv-stat">
                <tr> 
                    <td class="jlv-stat-key">Команд, получивших задание: </td> 
                    <td class="jlv-stat-value"><xsl:value-of select="quest/@got" /></td>
                </tr> <tr> 
                    <td class="jlv-stat-key"> Команд, сдавших задание: </td>
                    <td class="jlv-stat-value"><xsl:value-of select="quest/@done" /></td>
                </tr> <tr> 
                    <td class="jlv-stat-key">Пытались сдать: </td>
                    <td class="jlv-stat-value"><xsl:value-of select="quest/@tries" /></td>
                </tr> <tr>
                    <td class="jlv-stat-key">Время последней попытки: </td>
                    <td class="jlv-stat-value"><xsl:value-of select="quest/@last" /></td>
                </tr>
            </table>
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
