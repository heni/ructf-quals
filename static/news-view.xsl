<?xml version="1.0" encoding="UTF-8" ?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:template match="view[@type='news']">
        <xsl:variable name="username"><xsl:value-of select="param[@name = 'username']/@value" /> </xsl:variable>
        <div class="page-header"><a href="login"><img src="static/images/main.png" /></a></div>
        <div class="page-inform"> 
            <p class="trail"><a href="monitor">скорборд</a></p>
            <xsl:for-each select="news">
                <p><span class="time"><xsl:value-of select="@time"/> (@<xsl:value-of select="@author" />)</span>
                    <xsl:copy-of select="*" />
                </p>
                <hr class="news" />
            </xsl:for-each>
        </div>
    </xsl:template>
</xsl:stylesheet>
