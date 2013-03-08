<?xml version="1.0" encoding="UTF-8" ?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:template match="view[@type='login']">
        <xsl:variable name="try-count"><xsl:value-of select="param[@name = 'count']/@value" /> </xsl:variable>
        <div class="page-header"><a href="monitor"><img src="static/images/main.png" /></a></div>
        <div style="margin: 0 0 10%"></div>
        <p id="error" class="error" style="text-align: center; height: 1em" >
            <xsl:if test="$try-count &gt; 0">Authorization string is invalid.</xsl:if>
        </p>

        <form id="login-form" method="post" action="login">
            <p style="text-align: right"> <label> Authorization string: </label>
                <input class="password" name="auth" type="password" size="30" />
                <input type="hidden" name="count" value="{$try-count}" />
                <input class="button" type="submit" value="Послать" />
            </p>

        </form>
    </xsl:template>
</xsl:stylesheet>
