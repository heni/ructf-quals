<?xml version="1.0" encoding="UTF-8" ?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:template match="view[@type='hello']">
        <xsl:variable name="username"><xsl:value-of select="param[@name = 'username']/@value" /> </xsl:variable>
        <xsl:variable name="userrole"><xsl:value-of select="param[@name = 'userrole']/@value" /> </xsl:variable>
        <div class="page-header"><a href="login"><img src="static/images/main.png" /></a></div>
        <div class="page-inform"> 
            <p style="text-align:center"><b>Welcome to the contest page, <xsl:value-of select="$username" />!</b>
            </p>
            <xsl:choose>
                <xsl:when test="$userrole = 'team'">
                    <p> Here you can start to solve <a href="quest">tasks</a>, look at <a href="monitor">scoreboard</a>,
                       read <a href="news">news</a> or just <a href="signout">drink tea</a> :)
                    </p>
                </xsl:when>
                <xsl:when test="$userrole = 'org'">
                    <p> Добро пожаловать в центр управления <s>полётами</s> соревнованием! Можно посмотреть 
                        общий <a href="monitor">скорборд</a>, почитать/написать <a href="news">новости</a>
                        или просто <a href="signout">выпить чая</a> :)
                    </p>
                </xsl:when>
                <xsl:when test="$userrole = 'guest'">
                    <p> We don't know how you could be here. Please send full report with screenshots (with blackjack and hookers) to jury</p>
                </xsl:when>
            </xsl:choose>
        </div>
    </xsl:template>
</xsl:stylesheet>
