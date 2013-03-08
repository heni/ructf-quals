<?xml version="1.0" encoding="UTF-8" ?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:template match="view[@type = 'error']">
        <div class="page-header"><a href="login"><img src="static/images/main.png" /></a></div>
        <div style="margin: 0"></div>
        <pre id="error" class="error" style="text-align: left; min-height: 1em" >
            <xsl:value-of select="." />
        </pre>
    </xsl:template>
</xsl:stylesheet>
