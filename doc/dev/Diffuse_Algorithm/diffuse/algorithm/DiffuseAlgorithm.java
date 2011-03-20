package diffuse.algorithm;

import java.util.List;

import diffuse.Song;
import diffuse.SongAttribute;

public interface DiffuseAlgorithm {
	
	/**
	 * Diffuse a list of Songs by the given SongAttribute attribute
	 * @param inputList
	 * @return A diffused list
	 */
	public List<Song> diffuse(List<Song> inputList, SongAttribute attribute);
}
