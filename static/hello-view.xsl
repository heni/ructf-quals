<?xml version="1.0" encoding="UTF-8" ?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:template match="view[@type='hello']">
        <xsl:variable name="username"><xsl:value-of select="param[@name = 'username']/@value" /> </xsl:variable>
        <div class="page-header"><a href="login"><img src="static/images/main.png" /></a></div>
        <div class="page-inform"> 
            <p style="text-align:center"><b>Добро пожаловать на страницу соревнований, <xsl:value-of select="$username" />!</b>
            </p>
            <p> Здесь вы можете приступить к решению <a href="quest">заданий</a>, посмотреть <a href="monitor">скорборд</a>,
                <a href="static/news.xml">новости</a> или просто <a href="signout">выпить чая</a> :)
            </p>
        </div>
    </xsl:template>
</xsl:stylesheet>
