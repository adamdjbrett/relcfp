---
layout: null
---

var idx = lunr(function () {
  this.field('title', {boost: 10})
  this.field('excerpt')
  this.field('categories')
  this.field('tags')
  this.ref('id')
});

{% assign count = 0 %}
{% for c in site.collections %}
  {% assign docs = c.docs | where_exp:'doc','doc.search != false' %}
  {% for doc in docs %}
    idx.add({
      title: {{ doc.title | jsonify }},
      excerpt: {{ doc.content | strip_html | truncatewords: 50 | jsonify }},
      categories: {{ doc.categories | jsonify }},
      tags: {{ doc.tags | jsonify }},
      id: {{ count }}
    });
    {% assign count = count | plus: 1 %}
  {% endfor %}
{% endfor %}

var store = [
  {% for c in site.collections %}
    {% if forloop.last %}
      {% assign l = true %}
    {% endif %}
    {% assign docs = c.docs | where_exp:'doc','doc.search != false' %}
    {% for doc in docs %}
      {% if doc.header.teaser %}
        {% capture teaser %}{{ doc.header.teaser }}{% endcapture %}
      {% else %}
        {% assign teaser = site.teaser %}
      {% endif %}
      {
        "title": {{ doc.title | jsonify }},
        "url": {{ doc.url | relative_url | jsonify }},
        {% if doc.date %}
        "date": {{doc.date | date: "%B %d, %Y" | jsonify }},
        {% endif %}

        {% assign words_per_minute = site.words_per_minute | default: 200 %}

        {% assign words = doc.content | strip_html | number_of_words %}
      
        {% if words < words_per_minute %}
        {% assign timeRead = "less than 1 minute read" %}
       {% elsif words == words_per_minute %}
        {% assign timeRead = "1 minute read" %}
       {% else %}
        {% assign timeRead = words | divided_by: words_per_minute | append: " minute read" %}
       {% endif %}

        "timeRead": {{ timeRead | jsonify }},
        {% if doc.excerpt %}
        "excerpt": {{ doc.excerpt | strip_html | jsonify }},
        {% else %}
        "excerpt": {{ doc.content | strip_html | truncatewords: 50 |jsonify }},
        {% endif %}
        "teaser":
          {% if teaser contains "://" %}
            {{ teaser | jsonify }}
          {% else %}
            {{ teaser | relative_url | jsonify }}
          {% endif %}
      }{% unless forloop.last and l %},{% endunless %}
    {% endfor %}
  {% endfor %}]

$(document).ready(function() {
  $('input#search').on('keyup', function () {
    var resultdiv = $('#search-results');
    var query = $(this).val();
    var result = idx.search(query);
    $('#closer').click(function(){
       resultdiv.empty();
       $('#closer').hide();
    });
    $('#closer').show();
    resultdiv.empty();
    resultdiv.prepend('<hr><p class="results__found">'+result.length+' {{ site.data.ui-text[site.locale].results_found | default: "Result(s) found" }}</p>');
    for (var item in result) {
      var ref = result[item].ref;
      if(store[ref].teaser){
        var searchitem =
          '<div class="list__item">'+
            '<article class="archive__item" itemscope itemtype="http://schema.org/CreativeWork">'+
              '<h3 class="archive__item-title" itemprop="headline">'+
                '<a href="'+store[ref].url+'" rel="permalink" style="color: #1c1544">'+store[ref].title+'</a>'+
              '</h3>'+
              '<small>' + store[ref].date + " " + store[ref].timeRead +'</small>' + 

              '<div class="archive__item-teaser">'+
                '<img src="'+store[ref].teaser+'" alt="illustration">'+
              '</div>'+
              '<p class="archive__item-excerpt" itemprop="excerpt">'+store[ref].excerpt+'</p>'+
            '</article>'+
          '</div>';
      }
      else{
    	  var searchitem =
          '<div class="list__item">'+
            '<article class="archive__item" itemscope itemtype="http://schema.org/CreativeWork">'+
              '<h3 class="archive__item-title" itemprop="headline">'+
                '<a href="'+store[ref].url+'" rel="permalink" style="color: #1c1544">'+store[ref].title+'</a>'+
              '</h3>'+              '<small>' + store[ref].date + '</small>'+
              '<p class="archive__item-excerpt" itemprop="excerpt">'+store[ref].excerpt+ '</p>'+
            '</article>'+
          '</div>';
      }
      resultdiv.append(searchitem);
    }
    resultdiv.append("<hr style='margin-bottom: 40px'>");
    document.body.scrollTop = 0; // For Safari
    document.documentElement.scrollTop = 0; // For Chrome, Firefox, IE and Opera
  });
});






