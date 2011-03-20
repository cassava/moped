package diffuse;

import java.util.HashMap;
import java.util.Map;

public class Song {
	private Map<SongAttribute, String> attributes;

	public Song(String title, String artist, String album) {
		attributes = new HashMap<SongAttribute, String>(3);
		set(SongAttribute.TITLE, title);
		set(SongAttribute.ARTIST, artist);
		set(SongAttribute.ALBUM, album);
	}
	
	public String toString() {
		return get(SongAttribute.TITLE) + "by " +
				get(SongAttribute.ARTIST) + " (" +
				get(SongAttribute.ALBUM) + ").";
	}
	
	/**
	 * Set a song attribute.
	 * @param key the song attribute to set
	 * @param value the value to set the attribute to
	 * @return old song attribute value
	 */
	public String set(SongAttribute key, String value) {
		return attributes.put(key, value);
	}
	
	/**
	 * Get a song attribute.
	 * @param key the song attribute to get
	 * @return the value of the song attribute, or null if it is not set
	 */
	public String get(SongAttribute key) {
		return attributes.get(key);
	}
}
