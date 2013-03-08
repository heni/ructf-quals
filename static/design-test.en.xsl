<?xml version="1.0" encoding="UTF-8" ?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:template name="design-test">
        <div class="page-wrapper">
            <div class="page-header">Quest Server</div>
            <table class="quest-selector"> 
                <tr>
                    <td> 
                        <ul>
                            Admin
                            <li class="available" onclick="showQuest('admin100');"> 100 </li>
                            <li class="unavailable"> 200 </li>
                            <li class="unavailable"> 300 </li>
                        </ul>
                    </td>
                    <td> 
                        <ul>
                            Crack-the-box
                            <li class="available" onclick="showQuest('ctb100');"> 100 </li>
                            <li class="unavailable"> 200 </li>
                            <li class="unavailable"> 300 </li>
                        </ul>
                    </td>
                    <td>
                        <ul> 
                            Crypto+Stegano
                            <li class="available" onclick="showQuest('crypto200');"> 100 </li>
                            <li class="unavailable"> 200 </li>
                            <li class="unavailable"> 300 </li>
                        </ul>
                    </td>
                    <td> 
                        <ul>
                            Forensics
                            <li class="completed"> 100 </li>
                            <li class="available" onclick="showQuest('forensics200');"> 200 </li>
                            <li class="unavailable"> 300 </li>
                        </ul>
                    </td>
                   <td> 
                        <ul>
                            Joy
                            <li class="available" onclick="showQuest('joy100');"> 100 </li>
                            <li class="unavailable"> 200 </li>
                            <li class="unavailable"> 300 </li>
                        </ul>
                    </td>
                   <td> 
                        <ul>
                            PPC
                            <li class="available" onclick="showQuest('ppc100');"> 100 </li>
                            <li class="unavailable"> 200 </li>
                            <li class="unavailable"> 300 </li>
                        </ul>
                    </td>
                   <td> 
                        <ul>
                            Quests
                            <li class="completed"> 100 </li>
                            <li class="completed"> 200 </li>
                            <li class="completed"> 300 </li>
                        </ul>
                    </td>
                   <td> 
                        <ul>
                            Reverse
                            <li class="unavailable"> 100 </li>
                            <li class="unavailable"> 200 </li>
                            <li class="unavailable"> 300 </li>
                        </ul>
                    </td>
                 </tr>
            </table>
            <div class="page-pusher"></div>
        </div>
        <div class="page-footer"> &#169;RuCTF team 2009 </div>
        <xsl:call-template name="hidden-blocks" />
    </xsl:template>
    <xsl:template name="hidden-blocks">
        <div class="hidden">
            <div id="show-quest-block">
               Simple text 
            </div>
        </div> 
    </xsl:template>
</xsl:stylesheet>
