package diffuse.algorithm;

import java.util.List;

import diffuse.Song;
import diffuse.SongAttribute;

/**
 * The Atomic diffuse algorithm treats each Song as an entity that wants
 * to be as far away from the other songs in its group. The algorithm
 * iterates over the playlist, gradually moving same songs away from each
 * other until the desired separation threshhold has been reached.
 * 
 * <p>This algorithm is more akin to a natural process, and is such more
 * random and configurable, as well, given enough iterations, exact.
 * The runtime of this algorithm is quite long however.</p>
 * 
 * <p>Runtime: exponential runtime.</p>
 * 
 * <p>Algorithm:</p>
 * <ol>
 * <li>The list is first shuffled, so that the songs are already a
 *     little bit diffused. This reduces the runtime and is also required
 *     for randomness.</li>
 * </ol>
 * 
 * @author Ben Morgan
 *
 */
public class AtomicDiffuse implements DiffuseAlgorithm {

	@Override
	public List<Song> diffuse(List<Song> inputList, SongAttribute attribute) {
		// TODO Auto-generated method stub
		throw new RuntimeException("Not Implemented Error!");
	}

}
