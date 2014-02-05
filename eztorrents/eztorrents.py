#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import webbrowser
import sys
import argparse
import tpb

def argparser():
	parser = argparse.ArgumentParser(description='Fetch magnet links from TPB and open them with your preferred handler.')
	parser.add_argument('title', metavar='title', type=str,
	                   help='title of the torrent')
	parser.add_argument('-res', dest='resolution', type=str, default = '',
	                   help='specify resolution (e.g. 720p, 1080p)')
	return vars(parser.parse_args())


def gettoptorrents(args, search, maxseed):
	""" Returns the top 10 torrents (by seeders) of the category
	of the search passed to it"""

	torrents = {}
	found = 0
	for count, torrent in enumerate(search.order(tpb.ORDERS.SEEDERS.DES)):
		if maxseed and maxseed <= torrent.seeders:
			continue
		elif args['resolution'] in torrent.title:
			torrents[torrent.seeders] = torrent
			found += 1
		if found >= 10 or count >= 50:
			return torrents

def search(bayobject, title, category=False):
	""" Returns a TPB search object of a specific category if specified"""

	if category == 'HD':
		category = tpb.CATEGORIES.VIDEO.HD_MOVIES
	else:
		category = tpb.CATEGORIES.VIDEO.MOVIES
	return bayobject.search(title, category=category).multipage()

def gettop10torrents(*toptorrents):
	""" Takes two dictionaries of torrents and return the top 10 (by seeders).
	This is necessary because TPB differentiates between HD movies and "standard" movies"""

	torrents = toptorrents[0]
	torrents.update(toptorrents[1])
	seeders = torrents.keys()
	seeders.sort(reverse = True)
	top = {}
	for seedcount in seeders[:11]:
		top[seedcount] = torrents[seedcount]
	return top


def main():
	args = argparser()
	title = args["title"]
	piratebay = tpb.TPB("http://pirateproxy.net")
	HDsearch  = search(piratebay, title, "HD")
	stdSearch = search(piratebay, title)
	maxseed = 0
	rank = 0
	magnets = {}
	while True:
		topHD = gettoptorrents(args, HDsearch, maxseed)
		topSTD = gettoptorrents(args, stdSearch, maxseed)
		toptorrents = gettop10torrents(topHD, topSTD)
		topseeders = toptorrents.keys()
		topseeders.sort(reverse = True)

		for seedcount in topseeders:
			torrent = toptorrents[seedcount]
			magnets[rank] = torrent.magnet_link
			print("({}) Title: {}".format(rank, torrent.title.encode('utf-8')))
			print("    Seeders: {}, leechers: {} ".format(seedcount, torrent.leechers))
			rank += 1

		choice = input("Enter the number of the torrent you wish to download or -1 to see more: ")
		while choice not in list(range(rank)) and choice != -1:
			choice = input("Invalid option, try again: ")
		if choice == -1:
			maxseed = seedcount
		else:
			magnet = magnets[choice]
			webbrowser.open(magnet)
			return

if __name__ == "__main__":
	main()