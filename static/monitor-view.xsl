<?xml version="1.0" encoding="UTF-8" ?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    
    <xsl:template match="view[@type = 'monitor']">
        <div class="page-header"><a href="login"><img src="static/images/monitor.png" /></a></div>
        <xsl:apply-templates select="stat" />
        <xsl:apply-templates select="ranklist" />
        <form style="display:none" action="quest/get" id="post-form" name="post-form" method="POST">
            <input type="hidden" name="questId" />
        </form>
    </xsl:template>

    <xsl:template match="view[@type = 'monitor']/stat">
        <table class="quest-monitor">
            <tr><xsl:apply-templates select="category" /></tr>
        </table>
    </xsl:template>

    <xsl:template match="view[@type = 'monitor']/stat/category">
        <td>
            <ul><xsl:value-of select="@name" />
                <xsl:for-each select="quest">
                    <li class="{@status}">
                        <xsl:if test="@status = 'postponed'">
                            <xsl:attribute name="title">Есть ответы (<xsl:value-of select="@postponed" />), ожидающие решения</xsl:attribute>
                            <xsl:attribute name="onclick">showQuest('<xsl:value-of select="@id" />');</xsl:attribute>
                        </xsl:if>
                        <xsl:if test="@status = 'j-available' or @status = 'j-unavailable'">
                            <xsl:attribute name="onclick">showQuest('<xsl:value-of select="@id" />');</xsl:attribute>
                        </xsl:if>
                        <xsl:value-of select="concat(@label, ' (', @done, '&#160;done)')" /> 
                    </li>
                </xsl:for-each>
            </ul>
        </td>
    </xsl:template>
    
    <xsl:template match="view[@type = 'monitor']/ranklist">
        <table class="ranklist"> 
            <tr><th /><th>Team</th><th>Score</th></tr>
            <xsl:for-each select="team[@score &gt; 0]">
                <tr>
                    <td class="teampos"><xsl:value-of select="count(../team[@score > current()/@score]) + 1" /></td>
                    <td class="teamname"><xsl:value-of select="@name" /></td> 
                    <td class="teamscore"><xsl:value-of select="@score" /> </td>
                </tr>
            </xsl:for-each>
        </table>
    </xsl:template>

</xsl:stylesheet>
