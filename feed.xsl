<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:template match="/">
    <html>
      <head>
        <style>
          entry{
            padding-bottom: 10px; 
            margin-left: auto; 
            margin-right: auto; 
            max-width: 1200px; 
            display: grid; 
          }
          main{
            padding-bottom: 10px; 
            margin-left: auto; 
            margin-right: auto; 
            max-width: 1200px; 
            display: grid; 
          }
          p {
            margin-block-start: 0.5em;
            margin-block-end: 0.5em;
            font-size: 1rem;
          }
          title {
            margin-block-start: 0.1em;
            margin-block-end: 0.1em;
            font-size: 1.4rem;
          }
          h2 {
            margin-block-start: 0.1em;
            margin-block-end: 0.1em;
            font-size: 1.4rem;
          }
          .feed {
            display: grid;
            gap: 20px;
          }
          @media (min-width: 1024px) {
            .feed {
              grid-template-columns: 1fr 1fr;
            }
          }
          .feed_card {
            position: relative;
            display: grid;
            padding: 10px;
            border: 1px solid #012044;
            border-radius: 5px;
            box-shadow: 2px 4px 16px #ddd;
          }
          .feed_card_inner::after {
            content: "";
            background-image: linear-gradient( to bottom, transparent, transparent 60%, #fff 100%);
            position: absolute;
            bottom: 0;
            border-radius: 8px;
            left: 0;
            right: 0;
            height: 50%;
            width: 100%;
          }
            .feed_card:hover {
            transform: scale(1.01);
            box-shadow: 2px 3px 3px #bb45302d;
          }
          .feed_card_inner {
            height: 350px;
            overflow-y: hidden;
            word-break: break-word;
            display: grid;
            gap: 10px;
            align-content: start;
          }
          .feed_description{
            font-family: 'Futura';
            font-size: 0.8rem;
            line-height: 1.1;
          }
          small{
            font-size: 0.9rem;
            font-family: 'Futura';
          }
          @media (min-width: 550px) {
            main{
            padding: 0 10px 10px;
            }
            .feed {
            gap: 30px;
          }
            .feed_card_inner {
            height: 500px;
            }
            .feed_description{
              font-size: 1.15rem;
            }
            small{
              font-size: 0.9rem;
            }
            .feed_card {
              padding: 26px;
              border: 1px solid #012044;
              border-radius: 8px;
              box-shadow: 2px 4px 16px #ddd;
            }
          }
          @media (min-width: 768px){
            padding: 0 30px 30px;
          }
        </style>
      </head>
      <body>
        <main>
          <div class="feed">
            <xsl:for-each select="rss/channel/item">
              <div class="feed_card">
                <div class="feed_card_inner">
                <a>
                  <xsl:attribute name="href">
                    <xsl:value-of select="link" />
                  </xsl:attribute>
                <h3>
                  <xsl:value-of select="title" />
                </h3>
                </a>
                <small>
                  <span>Publication date:
                  <b>
                    <xsl:value-of select="pubDate" />
                  </b>
                  </span>
                </small>
                
                <div class="feed_description">
                  <xsl:value-of select="description" />
                </div>
                </div>
              </div>
            </xsl:for-each>
          </div>
        </main>
      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>