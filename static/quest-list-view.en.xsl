<?xml version="1.0" encoding="UTF-8" ?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    
    <xsl:template match="view[@type = 'quest-list']">
        <div class="page-header"><a href="login"><img src="static/images/main.png" /></a></div>
        <table class="quest-selector">
            <tr><xsl:apply-templates select="category" /></tr>
        </table>
        <form style="display:none" action="quest/get" id="post-form" name="post-form" method="POST">
            <input type="hidden" name="questId" />
        </form>
    </xsl:template>

    <xsl:template match="view[@type = 'quest-list']/category">
        <td>
            <ul><xsl:value-of select="@name" />
                <xsl:apply-templates select="quest" />
            </ul>
        </td>
    </xsl:template>
    
    <xsl:template match="view[@type = 'quest-list']/category/quest[@status = 'available']">
        <li class="{@status}" onclick="showQuest('{@id}');">
            <xsl:value-of select="@label" />
        </li>
    </xsl:template>

    <xsl:template match="view[@type = 'quest-list']/category/quest[@status != 'available']">
        <li class="{@status}" >
            <xsl:value-of select="@label" />
        </li>
    </xsl:template>

</xsl:stylesheet>
