/**
 * Author......: See docs/credits.txt
 * License.....: MIT
 */

//#define NEW_SIMD_CODE

#ifdef KERNEL_STATIC
#include M2S(INCLUDE_PATH/inc_vendor.h)
#include M2S(INCLUDE_PATH/inc_types.h)
#include M2S(INCLUDE_PATH/inc_platform.cl)
#include M2S(INCLUDE_PATH/inc_common.cl)
#include M2S(INCLUDE_PATH/inc_rp_optimized.h)
#include M2S(INCLUDE_PATH/inc_rp_optimized.cl)
#include M2S(INCLUDE_PATH/inc_simd.cl)
#include M2S(INCLUDE_PATH/inc_cipher_des.cl)
#endif

#if   VECT_SIZE == 1
#define BOX1(i,S) (S)[(i)]
#elif VECT_SIZE == 2
#define BOX1(i,S) make_u32x ((S)[(i).s0], (S)[(i).s1])
#elif VECT_SIZE == 4
#define BOX1(i,S) make_u32x ((S)[(i).s0], (S)[(i).s1], (S)[(i).s2], (S)[(i).s3])
#elif VECT_SIZE == 8
#define BOX1(i,S) make_u32x ((S)[(i).s0], (S)[(i).s1], (S)[(i).s2], (S)[(i).s3], (S)[(i).s4], (S)[(i).s5], (S)[(i).s6], (S)[(i).s7])
#elif VECT_SIZE == 16
#define BOX1(i,S) make_u32x ((S)[(i).s0], (S)[(i).s1], (S)[(i).s2], (S)[(i).s3], (S)[(i).s4], (S)[(i).s5], (S)[(i).s6], (S)[(i).s7], (S)[(i).s8], (S)[(i).s9], (S)[(i).sa], (S)[(i).sb], (S)[(i).sc], (S)[(i).sd], (S)[(i).se], (S)[(i).sf])
#endif

KERNEL_FQ KERNEL_FA void m14000_mxx (KERN_ATTR_RULES ())
{
  /**
   * base
   */

  const u64 gid = get_global_id (0);
  const u64 lid = get_local_id (0);
  const u64 lsz = get_local_size (0);

  /**
   * shared
   */

  LOCAL_VK u32 s_SPtrans[8][64];
  LOCAL_VK u32 s_skb[8][64];

  for (u32 i = lid; i < 64; i += lsz)
  {
    s_SPtrans[0][i] = c_SPtrans[0][i];
    s_SPtrans[1][i] = c_SPtrans[1][i];
    s_SPtrans[2][i] = c_SPtrans[2][i];
    s_SPtrans[3][i] = c_SPtrans[3][i];
    s_SPtrans[4][i] = c_SPtrans[4][i];
    s_SPtrans[5][i] = c_SPtrans[5][i];
    s_SPtrans[6][i] = c_SPtrans[6][i];
    s_SPtrans[7][i] = c_SPtrans[7][i];

    s_skb[0][i] = c_skb[0][i];
    s_skb[1][i] = c_skb[1][i];
    s_skb[2][i] = c_skb[2][i];
    s_skb[3][i] = c_skb[3][i];
    s_skb[4][i] = c_skb[4][i];
    s_skb[5][i] = c_skb[5][i];
    s_skb[6][i] = c_skb[6][i];
    s_skb[7][i] = c_skb[7][i];
  }

  SYNC_THREADS ();

  if (gid >= GID_CNT) return;

  /**
   * base
   */

  u32 pw_buf0[4];
  u32 pw_buf1[4];

  pw_buf0[0] = pws[gid].i[ 0];
  pw_buf0[1] = pws[gid].i[ 1];
  pw_buf0[2] = 0;
  pw_buf0[3] = 0;
  pw_buf1[0] = 0;
  pw_buf1[1] = 0;
  pw_buf1[2] = 0;
  pw_buf1[3] = 0;

  const u32 pw_len = pws[gid].pw_len;

  /**
   * salt
   */

  u32 salt_buf0[2];

  salt_buf0[0] = salt_bufs[SALT_POS_HOST].salt_buf_pc[0];
  salt_buf0[1] = salt_bufs[SALT_POS_HOST].salt_buf_pc[1];

  /**
   * main
   */

  for (u32 il_pos = 0; il_pos < IL_CNT; il_pos += VECT_SIZE)
  {
    u32 w0[4] = { 0 };
    u32 w1[4] = { 0 };
    u32 w2[4] = { 0 };
    u32 w3[4] = { 0 };

    apply_rules_vect_optimized (pw_buf0, pw_buf1, pw_len, rules_buf, il_pos, w0, w1);

    const u32 c = w0[0];
    const u32 d = w0[1];

    u32 Kc[16];
    u32 Kd[16];

    _des_crypt_keysetup (c, d, Kc, Kd, s_skb);

    u32 data[2];

    data[0] = salt_buf0[0];
    data[1] = salt_buf0[1];

    u32 iv[2];

    _des_crypt_encrypt_noipfp (iv, data, Kc, Kd, s_SPtrans);

    u32 z = 0;

    COMPARE_M_SIMD (iv[0], iv[1], z, z);
  }
}

KERNEL_FQ KERNEL_FA void m14000_sxx (KERN_ATTR_RULES ())
{
  /**
   * base
   */

  const u64 gid = get_global_id (0);
  const u64 lid = get_local_id (0);
  const u64 lsz = get_local_size (0);

  /**
   * shared
   */

  LOCAL_VK u32 s_SPtrans[8][64];
  LOCAL_VK u32 s_skb[8][64];

  for (u32 i = lid; i < 64; i += lsz)
  {
    s_SPtrans[0][i] = c_SPtrans[0][i];
    s_SPtrans[1][i] = c_SPtrans[1][i];
    s_SPtrans[2][i] = c_SPtrans[2][i];
    s_SPtrans[3][i] = c_SPtrans[3][i];
    s_SPtrans[4][i] = c_SPtrans[4][i];
    s_SPtrans[5][i] = c_SPtrans[5][i];
    s_SPtrans[6][i] = c_SPtrans[6][i];
    s_SPtrans[7][i] = c_SPtrans[7][i];

    s_skb[0][i] = c_skb[0][i];
    s_skb[1][i] = c_skb[1][i];
    s_skb[2][i] = c_skb[2][i];
    s_skb[3][i] = c_skb[3][i];
    s_skb[4][i] = c_skb[4][i];
    s_skb[5][i] = c_skb[5][i];
    s_skb[6][i] = c_skb[6][i];
    s_skb[7][i] = c_skb[7][i];
  }

  SYNC_THREADS ();

  if (gid >= GID_CNT) return;

  /**
   * base
   */

  u32 pw_buf0[4];
  u32 pw_buf1[4];

  pw_buf0[0] = pws[gid].i[ 0];
  pw_buf0[1] = pws[gid].i[ 1];
  pw_buf0[2] = 0;
  pw_buf0[3] = 0;
  pw_buf1[0] = 0;
  pw_buf1[1] = 0;
  pw_buf1[2] = 0;
  pw_buf1[3] = 0;

  const u32 pw_len = pws[gid].pw_len;

  /**
   * salt
   */

  u32 salt_buf0[2];

  salt_buf0[0] = salt_bufs[SALT_POS_HOST].salt_buf_pc[0];
  salt_buf0[1] = salt_bufs[SALT_POS_HOST].salt_buf_pc[1];

  /**
   * digest
   */

  const u32 search[4] =
  {
    digests_buf[DIGESTS_OFFSET_HOST].digest_buf[DGST_R0],
    digests_buf[DIGESTS_OFFSET_HOST].digest_buf[DGST_R1],
    0,
    0
  };

  /**
   * main
   */

  for (u32 il_pos = 0; il_pos < IL_CNT; il_pos += VECT_SIZE)
  {
    u32 w0[4] = { 0 };
    u32 w1[4] = { 0 };
    u32 w2[4] = { 0 };
    u32 w3[4] = { 0 };

    apply_rules_vect_optimized (pw_buf0, pw_buf1, pw_len, rules_buf, il_pos, w0, w1);

    const u32 c = w0[0];
    const u32 d = w0[1];

    u32 Kc[16];
    u32 Kd[16];

    _des_crypt_keysetup (c, d, Kc, Kd, s_skb);

    u32 data[2];

    data[0] = salt_buf0[0];
    data[1] = salt_buf0[1];

    u32 iv[2];

    _des_crypt_encrypt_noipfp (iv, data, Kc, Kd, s_SPtrans);

    u32 z = 0;

    COMPARE_S_SIMD (iv[0], iv[1], z, z);
  }
}
