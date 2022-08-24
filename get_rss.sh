wget -O feed.xml 'https://input.relcfp.com/p/i/?a=rss&rid=6304038b62d7d&user=wyattphd-admin&token=b5142b8a9c4208e145af4be2c86d4ad4&hours=168'
sed -i 's/<!\[CDATA\[//g' feed.xml
sed -i 's/]]>//g' feed.xml
sed -i 's/<br>/<br\/>/g' feed.xml