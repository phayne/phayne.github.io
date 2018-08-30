---
layout: page
permalink: /publications/
title: publications
description: Peer-reviewed publications in chronological order.
years: [2018,2017,2016,2015,2014,2013,2012,2010,2009,2008]
---

{% for y in page.years %}
  <h3 class="year">{{y}}</h3>
  {% bibliography -f papers -q @*[year={{y}}]* %}
{% endfor %}
