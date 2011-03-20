package diffuse.algorithm;

import java.util.List;

import diffuse.Song;
import diffuse.SongAttribute;

/**
 * The Rigid Sandglass diffuse algorithm is similar to the Sandglass algorithm,
 * except that it does not choose the song randomly from a pool, but picks
 * very deterministicly when a song should be inserted into the list.
 * This results in a diffusion which is very quick and exact, but less random.
 * 
 * <p>Runtime: O(n) linear runtime.</p>
 * 
 * <p>Algorithm:</p>
 * <ol>
 * <li>Separate all of the songs by the song attribute grouping. This
 *     results in groups that we will name A, B, C, and so forth.</li>
 * <li>Find the biggest, divide its size by the sizes of all the others
 *     (including itself) and store this value with each group.</li>
 * <li>The division results determine when to place that value after so
 *     many songs have been placed.<br />
 *     Values have to be at least as much, so it needs to flow over,
 *     if they are not whole numbers. In that case, save the overflowed value.
 *     Such that:<br />
 *     place one A: add 1 to all the other storage values... etc
 *     If one is over it's limit, add it, save the rest for the next time.</li>
 * <li>Take the one that is most over its own limit. Or—prefer adding one that
 *     has a lower limit. Limit of A is 1.<br />
 *     Alternatively, if two are within ..x.. of the same amount over the limit,
 *     then prefer the one with the lower limit.</li>
 * </ol>
 * 
 * @author Ben Morgan
 *
 */
public class RigidSandglassDiffuse implements DiffuseAlgorithm {

	@Override
	public List<Song> diffuse(List<Song> inputList, SongAttribute attribute) {
		// TODO Auto-generated method stub
		throw new RuntimeException("Not Implemented Error!");
	}

}
