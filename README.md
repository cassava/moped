MPD Moped -- Driving your MPD playlists where they need to go!
=======================================================================

Moped is an advanced playlist manipulator for the Music Player Daemon,
also known as MPD. The purpose is to provide a flexible and easy way to
add music to the playlist, as well as perform other extra tasks


Examples (shamelessly copied from the man file)
-------------------------------------------------
  The most basic example of a Moped command would be to insert  a  single
  track into the playlist, by using the default operation and the default
  keyword:
      Landing in London

  Using a little bit more power from Moped, we could insert an album, all
  the songs from a particular artist, and two different tracks:
      b: Hatchery a: 3 Doors mt: "Breaking the Habit" "Easier to Run"

  Note  that,  because  we  have only been specifying keywords and search
  terms, we do not have to provide the full term, just part of it.

  Suppose that we want to remove a song from a particular artist:
      r<a: Red t: Pieces>

  Alternatively we could make it more complicated with another query:
      +<a:Linkin Park !t:Intro> r<b: Hybrid Theory>


Features
----------
  * Flexible messaging system
  * Flexible search functions
    - regex
    - filtering
    - grouping
    - easy syntax
    - dry search
  * Insert, append or remove songs
  * Add the database to the playlist
  * Blacklists
  * Shuffling
    - [ Intelligent shuffling ]
  * Configuration file support
  * Crop or clear the playlist
  * Withhold songs while cropping
  * Perform individual commands (such as only crop)
  * Gui messaging (moped -g is useful, bind it to a shortcut)


_Read the man file!_


_Revision: 18. November 2010_

