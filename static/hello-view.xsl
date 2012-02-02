<?xml version="1.0" encoding="UTF-8" ?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:template match="view[@type='hello']">
        <xsl:variable name="username"><xsl:value-of select="param[@name = 'username']/@value" /> </xsl:variable>
        <xsl:variable name="userrole"><xsl:value-of select="param[@name = 'userrole']/@value" /> </xsl:variable>
        <div class="page-header"><a href="login"><img src="static/images/main.png" /></a></div>
        <div class="page-inform"> 
            <p style="text-align:center"><b>Добро пожаловать на страницу соревнований, <xsl:value-of select="$username" />!</b>
            </p>
            <xsl:choose>
                <xsl:when test="$userrole = 'team'">
                    <p> Здесь вы можете приступить к решению <a href="quest">заданий</a>, посмотреть <a href="monitor">скорборд</a>,
                        <a href="news">новости</a> или просто <a href="signout">выпить чая</a> :)
                    </p>
                </xsl:when>
                <xsl:when test="$userrole = 'org'">
                    <p> Добро пожаловать в центр управления <s>полётами</s> соревнованием! Можно посмотреть 
                        общий <a href="monitor">скорборд</a>, почитать/написать <a href="news">новости</a>
                        или просто <a href="signout">выпить чая</a> :)
                    </p>
                </xsl:when>
                <xsl:when test="$userrole = 'guest'">
                    <p> Мы не знаем как вы здесь оказались. Пришлите подробные отчёт со скриншотами (блэкджеком и шлюхами) жюри</p>
                </xsl:when>
            </xsl:choose>
        </div>
    </xsl:template>
</xsl:stylesheet>
