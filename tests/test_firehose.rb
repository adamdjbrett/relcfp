require "rexml/document"

# Capture the real Jekyll hook without building the site for each fixture.
module Jekyll
  module Hooks
    def self.register(*, &hook)
      @hook = hook
    end

    def self.run(site)
      @hook.call(site)
    end
  end
end

require_relative "../_plugins/firehose"
Page = Struct.new(:url, :output)
Site = Struct.new(:pages, :config)
blank = '<author><name> </name></author>'
named = '<author><name>Source Author</name><uri>https://example.org/</uri></author>'

['', blank, named].each do |feed_author|
  authors = ['', blank, named, blank + named]
  entries = authors.each_with_index.map do |author, i|
    "<entry><id>https://example.org/#{i}</id><updated>2026-11-03T19:30:00Z</updated>#{author}</entry>"
  end.join
  firehose = Page.new('/firehose.xml', '<feed xmlns="http://www.w3.org/2005/Atom"/>')
  site = Site.new([firehose,
                   Page.new('/posts/feed.atom', '<feed/>'),
                   Page.new('/feed.xml', "<feed>#{feed_author}#{entries}</feed>")],
                  { 'author' => { 'name' => 'RELCFP' } })
  Jekyll::Hooks.run(site)
  result = REXML::Document.new(firehose.output).root.get_elements('entry')
  raise 'Lost entries with identical timestamps' unless result.size == authors.size
  result.each do |entry|
    i = entry.elements['id'].text.split('/').last.to_i
    expected = i >= 2 || feed_author == named ? 'Source Author' : 'RELCFP'
    names = entry.get_elements('author/name').map(&:text)
    raise "Unexpected authors: #{names.inspect}" unless names == [expected]
    if expected == 'Source Author'
      raise 'Lost source author URI' unless entry.elements['author/uri'].text == 'https://example.org/'
    end
    raise 'Changed timestamp' unless entry.elements['updated'].text == '2026-11-03T19:30:00Z'
  end
end
puts 'Firehose author fallbacks and timestamp preservation verified.'
