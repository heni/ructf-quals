<?xml version="1.0" encoding="UTF-8" ?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:template match="view[@type='news']">
        <xsl:variable name="editable"><xsl:value-of select="param[@name = 'editable']/@value" /></xsl:variable>
        <xsl:variable name="prevPage"><xsl:value-of select="param[@name = 'prevPage']/@value" /></xsl:variable>
        <xsl:variable name="nextPage"><xsl:value-of select="param[@name = 'nextPage']/@value" /></xsl:variable>
        <div class="page-header"><a href="login"><img src="static/images/news.png" /></a></div>
        <div class="page-inform"> 
            <p class="trail"><a href="monitor">scoreboard</a></p>
            <p style="text-align: center"> <b>Latest news</b></p>
            <xsl:for-each select="news">
                <p>
                    <span class="time"><xsl:value-of select="@time"/> (@<xsl:value-of select="@author" />)</span>
                    <xsl:copy-of select="*" />
                    <xsl:if test="$editable = 'true'">
                        <div class="news-del-btn button link" onclick="deleteNewsItem({@id});" >remove</div>
                    </xsl:if>
                </p>
                <hr class="news" />
            </xsl:for-each>
            <xsl:if test="$editable = 'true'">
                <div id="btn-panel">
                    <div class="news-add-btn button link" onclick="showPostForm('news/add');">add news</div>
                </div>
                <form action="" id="post-form" name="post-form" method="POST" >
                    <input type="hidden" name="event" value=""/>
                    <input type="hidden" name="page" value=""/>
                    <label>Enter text of news:</label> <br />
                    <textarea name="text" rows="5" style="width: 100%">
                    </textarea>
                    <input type="submit" value="Отправить" class="button" />
                </form> 
            </xsl:if>
            <div class="nav-wrapper">
                <xsl:if test="$prevPage != ''">
                    <div class="nav-prev"><span class="link" onclick="navigateNews({$prevPage});">«</span></div>
                </xsl:if>
                <xsl:if test="$nextPage != ''">
                    <div class="nav-next"><span class="link" onclick="navigateNews({$nextPage});">»</span></div>
                </xsl:if>
            </div>
        </div>
    </xsl:template>
</xsl:stylesheet>
