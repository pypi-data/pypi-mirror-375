/**
 * based on 3200
 *
 */

#ifdef KERNEL_STATIC
#include M2S(INCLUDE_PATH/inc_vendor.h)
#include M2S(INCLUDE_PATH/inc_types.h)
#include M2S(INCLUDE_PATH/inc_platform.cl)
#include M2S(INCLUDE_PATH/inc_common.cl)
#include M2S(INCLUDE_PATH/inc_cipher_blowfish.cl)
#endif

#define COMPARE_S M2S(INCLUDE_PATH/inc_comp_single.cl)
#define COMPARE_M M2S(INCLUDE_PATH/inc_comp_multi.cl)

typedef struct bcrypt_tmp
{
  u32 E[18];

  u32 P[18];

  u32 S0[256];
  u32 S1[256];
  u32 S2[256];
  u32 S3[256];

} bcrypt_tmp_t;

KERNEL_FQ KERNEL_FA void m33800_init (KERN_ATTR_TMPS (bcrypt_tmp_t))
{
  /**
   * base
   */

  const u64 gid = get_global_id (0);
  const u64 lid = get_local_id (0);

  if (gid >= GID_CNT) return;

  const u32 pw_len = pws[gid].pw_len;

  u32 w[18];

  w[ 0] = pws[gid].i[ 0];
  w[ 1] = pws[gid].i[ 1];
  w[ 2] = pws[gid].i[ 2];
  w[ 3] = pws[gid].i[ 3];
  w[ 4] = pws[gid].i[ 4];
  w[ 5] = pws[gid].i[ 5];
  w[ 6] = pws[gid].i[ 6];
  w[ 7] = pws[gid].i[ 7];
  w[ 8] = pws[gid].i[ 8];
  w[ 9] = pws[gid].i[ 9];
  w[10] = pws[gid].i[10];
  w[11] = pws[gid].i[11];
  w[12] = pws[gid].i[12];
  w[13] = pws[gid].i[13];
  w[14] = pws[gid].i[14];
  w[15] = pws[gid].i[15];
  w[16] = pws[gid].i[16];
  w[17] = pws[gid].i[17];

  u32 E[18] = { 0 };

  expand_key (E, w, pw_len);

  E[ 0] = hc_swap32_S (E[ 0]);
  E[ 1] = hc_swap32_S (E[ 1]);
  E[ 2] = hc_swap32_S (E[ 2]);
  E[ 3] = hc_swap32_S (E[ 3]);
  E[ 4] = hc_swap32_S (E[ 4]);
  E[ 5] = hc_swap32_S (E[ 5]);
  E[ 6] = hc_swap32_S (E[ 6]);
  E[ 7] = hc_swap32_S (E[ 7]);
  E[ 8] = hc_swap32_S (E[ 8]);
  E[ 9] = hc_swap32_S (E[ 9]);
  E[10] = hc_swap32_S (E[10]);
  E[11] = hc_swap32_S (E[11]);
  E[12] = hc_swap32_S (E[12]);
  E[13] = hc_swap32_S (E[13]);
  E[14] = hc_swap32_S (E[14]);
  E[15] = hc_swap32_S (E[15]);
  E[16] = hc_swap32_S (E[16]);
  E[17] = hc_swap32_S (E[17]);

  for (u32 i = 0; i < 18; i++)
  {
    tmps[gid].E[i] = E[i];
  }

  /**
   * salt
   */

  u32 salt_buf[4];

  salt_buf[0] = salt_bufs[SALT_POS_HOST].salt_buf[0];
  salt_buf[1] = salt_bufs[SALT_POS_HOST].salt_buf[1];
  salt_buf[2] = salt_bufs[SALT_POS_HOST].salt_buf[2];
  salt_buf[3] = salt_bufs[SALT_POS_HOST].salt_buf[3];

  #ifdef DYNAMIC_LOCAL
  // from host
  #else
  LOCAL_VK u32 S0_all[FIXED_LOCAL_SIZE][256];
  LOCAL_VK u32 S1_all[FIXED_LOCAL_SIZE][256];
  LOCAL_VK u32 S2_all[FIXED_LOCAL_SIZE][256];
  LOCAL_VK u32 S3_all[FIXED_LOCAL_SIZE][256];
  #endif

  #ifdef BCRYPT_AVOID_BANK_CONFLICTS
  LOCAL_AS u32 *S0 = S + (FIXED_LOCAL_SIZE * 256 * 0);
  LOCAL_AS u32 *S1 = S + (FIXED_LOCAL_SIZE * 256 * 1);
  LOCAL_AS u32 *S2 = S + (FIXED_LOCAL_SIZE * 256 * 2);
  LOCAL_AS u32 *S3 = S + (FIXED_LOCAL_SIZE * 256 * 3);
  #else
  LOCAL_AS u32 *S0 = S0_all[lid];
  LOCAL_AS u32 *S1 = S1_all[lid];
  LOCAL_AS u32 *S2 = S2_all[lid];
  LOCAL_AS u32 *S3 = S3_all[lid];
  #endif

  u32 P[18];

  blowfish_set_key_salt (E, 18, salt_buf, P, S0, S1, S2, S3);

  // store

  for (u32 i = 0; i < 18; i++)
  {
    tmps[gid].P[i] = P[i];
  }

  for (u32 i = 0; i < 256; i++)
  {
    tmps[gid].S0[i] = GET_KEY32 (S0, i);
    tmps[gid].S1[i] = GET_KEY32 (S1, i);
    tmps[gid].S2[i] = GET_KEY32 (S2, i);
    tmps[gid].S3[i] = GET_KEY32 (S3, i);
  }
}

KERNEL_FQ KERNEL_FA void m33800_loop (KERN_ATTR_TMPS (bcrypt_tmp_t))
{
  /**
   * base
   */

  const u64 gid = get_global_id (0);
  const u64 lid = get_local_id (0);

  if (gid >= GID_CNT) return;

  // load

  u32 E[18];

  for (u32 i = 0; i < 18; i++)
  {
    E[i] = tmps[gid].E[i];
  }

  u32 P[18];

  for (u32 i = 0; i < 18; i++)
  {
    P[i] = tmps[gid].P[i];
  }

  #ifdef DYNAMIC_LOCAL
  // from host
  #else
  LOCAL_VK u32 S0_all[FIXED_LOCAL_SIZE][256];
  LOCAL_VK u32 S1_all[FIXED_LOCAL_SIZE][256];
  LOCAL_VK u32 S2_all[FIXED_LOCAL_SIZE][256];
  LOCAL_VK u32 S3_all[FIXED_LOCAL_SIZE][256];
  #endif

  #ifdef BCRYPT_AVOID_BANK_CONFLICTS
  LOCAL_AS u32 *S0 = S + (FIXED_LOCAL_SIZE * 256 * 0);
  LOCAL_AS u32 *S1 = S + (FIXED_LOCAL_SIZE * 256 * 1);
  LOCAL_AS u32 *S2 = S + (FIXED_LOCAL_SIZE * 256 * 2);
  LOCAL_AS u32 *S3 = S + (FIXED_LOCAL_SIZE * 256 * 3);
  #else
  LOCAL_AS u32 *S0 = S0_all[lid];
  LOCAL_AS u32 *S1 = S1_all[lid];
  LOCAL_AS u32 *S2 = S2_all[lid];
  LOCAL_AS u32 *S3 = S3_all[lid];
  #endif

  for (u32 i = 0; i < 256; i++)
  {
    SET_KEY32 (S0, i, tmps[gid].S0[i]);
    SET_KEY32 (S1, i, tmps[gid].S1[i]);
    SET_KEY32 (S2, i, tmps[gid].S2[i]);
    SET_KEY32 (S3, i, tmps[gid].S3[i]);
  }

  /**
   * salt
   */

  u32 salt_buf[4];

  salt_buf[0] = salt_bufs[SALT_POS_HOST].salt_buf[0];
  salt_buf[1] = salt_bufs[SALT_POS_HOST].salt_buf[1];
  salt_buf[2] = salt_bufs[SALT_POS_HOST].salt_buf[2];
  salt_buf[3] = salt_bufs[SALT_POS_HOST].salt_buf[3];

  /**
   * main loop
   */

  for (u32 i = 0; i < LOOP_CNT; i++)
  {
    for (u32 i = 0; i < 18; i++)
    {
      P[i] ^= E[i];
    }

    blowfish_encrypt (P, S0, S1, S2, S3);

    P[ 0] ^= salt_buf[0];
    P[ 1] ^= salt_buf[1];
    P[ 2] ^= salt_buf[2];
    P[ 3] ^= salt_buf[3];
    P[ 4] ^= salt_buf[0];
    P[ 5] ^= salt_buf[1];
    P[ 6] ^= salt_buf[2];
    P[ 7] ^= salt_buf[3];
    P[ 8] ^= salt_buf[0];
    P[ 9] ^= salt_buf[1];
    P[10] ^= salt_buf[2];
    P[11] ^= salt_buf[3];
    P[12] ^= salt_buf[0];
    P[13] ^= salt_buf[1];
    P[14] ^= salt_buf[2];
    P[15] ^= salt_buf[3];
    P[16] ^= salt_buf[0];
    P[17] ^= salt_buf[1];

    blowfish_encrypt (P, S0, S1, S2, S3);
  }

  // store

  for (u32 i = 0; i < 18; i++)
  {
    tmps[gid].P[i] = P[i];
  }

  for (u32 i = 0; i < 256; i++)
  {
    tmps[gid].S0[i] = GET_KEY32 (S0, i);
    tmps[gid].S1[i] = GET_KEY32 (S1, i);
    tmps[gid].S2[i] = GET_KEY32 (S2, i);
    tmps[gid].S3[i] = GET_KEY32 (S3, i);
  }
}

KERNEL_FQ KERNEL_FA void m33800_init2 (KERN_ATTR_TMPS (bcrypt_tmp_t))
{
  /**
   * base
   */

  const u64 gid = get_global_id (0);
  const u64 lid = get_local_id (0);

  if (gid >= GID_CNT) return;

  const u32 pw_len = 60;

  /**
   * calculate final inner/first bcrypt
   */
  u32 P[18];

  for (u32 i = 0; i < 18; i++)
  {
    P[i] = tmps[gid].P[i];
  }

  #ifdef DYNAMIC_LOCAL
  // from host
  #else
  LOCAL_VK u32 S0_all[FIXED_LOCAL_SIZE][256];
  LOCAL_VK u32 S1_all[FIXED_LOCAL_SIZE][256];
  LOCAL_VK u32 S2_all[FIXED_LOCAL_SIZE][256];
  LOCAL_VK u32 S3_all[FIXED_LOCAL_SIZE][256];
  #endif

  #ifdef BCRYPT_AVOID_BANK_CONFLICTS
  LOCAL_AS u32 *S0 = S + (FIXED_LOCAL_SIZE * 256 * 0);
  LOCAL_AS u32 *S1 = S + (FIXED_LOCAL_SIZE * 256 * 1);
  LOCAL_AS u32 *S2 = S + (FIXED_LOCAL_SIZE * 256 * 2);
  LOCAL_AS u32 *S3 = S + (FIXED_LOCAL_SIZE * 256 * 3);
  #else
  LOCAL_AS u32 *S0 = S0_all[lid];
  LOCAL_AS u32 *S1 = S1_all[lid];
  LOCAL_AS u32 *S2 = S2_all[lid];
  LOCAL_AS u32 *S3 = S3_all[lid];
  #endif

  for (u32 i = 0; i < 256; i++)
  {
    SET_KEY32 (S0, i, tmps[gid].S0[i]);
    SET_KEY32 (S1, i, tmps[gid].S1[i]);
    SET_KEY32 (S2, i, tmps[gid].S2[i]);
    SET_KEY32 (S3, i, tmps[gid].S3[i]);
  }

  u32 L0;
  u32 R0;

  L0 = BCRYPTM_0;
  R0 = BCRYPTM_1;

  for (u32 i = 0; i < 64; i++)
  {
    BF_ENCRYPT (L0, R0);
  }

  const u32 r0 = L0;
  const u32 r1 = R0;

  L0 = BCRYPTM_2;
  R0 = BCRYPTM_3;

  for (u32 i = 0; i < 64; i++)
  {
    BF_ENCRYPT (L0, R0);
  }

  const u32 r2 = L0;
  const u32 r3 = R0;

  L0 = BCRYPTM_4;
  R0 = BCRYPTM_5;

  for (u32 i = 0; i < 64; i++)
  {
    BF_ENCRYPT (L0, R0);
  }

  const u32 r4 = L0;
  const u32 r5 = R0;

  u32 w[18];

  /**
   * set first bcrypt as input for second bcrypt
   */

  //put in the saved beginning and salt of original hash
  w[ 0] = salt_bufs[SALT_POS_HOST].salt_buf_pc[ 0];
  w[ 1] = salt_bufs[SALT_POS_HOST].salt_buf_pc[ 1];
  w[ 2] = salt_bufs[SALT_POS_HOST].salt_buf_pc[ 2];
  w[ 3] = salt_bufs[SALT_POS_HOST].salt_buf_pc[ 3];
  w[ 4] = salt_bufs[SALT_POS_HOST].salt_buf_pc[ 4];
  w[ 5] = salt_bufs[SALT_POS_HOST].salt_buf_pc[ 5];
  w[ 6] = salt_bufs[SALT_POS_HOST].salt_buf_pc[ 6];
  //w[ 7] = salt_bufs[SALT_POS_HOST].salt_buf_pc[ 7]; //here for logic (overwritten in next step)

  //now fill in base64; last Byte is zeroed (--> 0x00000F00 not 0x00000FC0)
  w[ 7] = salt_bufs[SALT_POS_HOST].salt_buf_pc[ 7] ^ (c_bcrypt_base64_alphabet[(r0&0xFC000000)>>26] << 8) ^ (c_bcrypt_base64_alphabet[(r0&0x03F00000)>> 20] << 16) ^ (c_bcrypt_base64_alphabet[(r0&0x000FC000)>>14] << 24);
  w[ 8] = c_bcrypt_base64_alphabet[(r0&0x00003F00)>> 8] ^ (c_bcrypt_base64_alphabet[(r0&0x000000FC)>> 2] << 8) ^ (c_bcrypt_base64_alphabet[(r0&0x00000003)<< 4 ^ (r1&0xF0000000)>>28] << 16) ^ (c_bcrypt_base64_alphabet[(r1&0x0FC00000)>>22] << 24);
  w[ 9] = c_bcrypt_base64_alphabet[(r1&0x003F0000)>>16] ^ (c_bcrypt_base64_alphabet[(r1&0x0000FC00)>>10] << 8) ^ (c_bcrypt_base64_alphabet[(r1&0x000003F0)>> 4] << 16) ^ (c_bcrypt_base64_alphabet[(r1&0x0000000F)<< 2 ^ (r2&0xC0000000)>>30] << 24);
  w[10] = c_bcrypt_base64_alphabet[(r2&0x3F000000)>>24] ^ (c_bcrypt_base64_alphabet[(r2&0x00FC0000)>>18] << 8) ^ (c_bcrypt_base64_alphabet[(r2&0x0003F000)>>12] << 16) ^ (c_bcrypt_base64_alphabet[(r2&0x00000FC0)>> 6] << 24);
  w[11] = c_bcrypt_base64_alphabet[(r2&0x0000003F)    ] ^ (c_bcrypt_base64_alphabet[(r3&0xFC000000)>>26] << 8) ^ (c_bcrypt_base64_alphabet[(r3&0x03F00000)>>20] << 16) ^ (c_bcrypt_base64_alphabet[(r3&0x000FC000)>>14] << 24);
  w[12] = c_bcrypt_base64_alphabet[(r3&0x00003F00)>> 8] ^ (c_bcrypt_base64_alphabet[(r3&0x000000FC)>> 2] << 8) ^ (c_bcrypt_base64_alphabet[(r3&0x00000003)<< 4 ^ (r4&0xF0000000)>>28] << 16) ^ (c_bcrypt_base64_alphabet[(r4&0x0FC00000)>>22] << 24);
  w[13] = c_bcrypt_base64_alphabet[(r4&0x003F0000)>>16] ^ (c_bcrypt_base64_alphabet[(r4&0x0000FC00)>>10] << 8) ^ (c_bcrypt_base64_alphabet[(r4&0x000003F0)>> 4] << 16) ^ (c_bcrypt_base64_alphabet[(r4&0x0000000F)<< 2 ^ (r5&0xC0000000)>>30] << 24);
  w[14] = c_bcrypt_base64_alphabet[(r5&0x3F000000)>>24] ^ (c_bcrypt_base64_alphabet[(r5&0x00FC0000)>>18] << 8) ^ (c_bcrypt_base64_alphabet[(r5&0x0003F000)>>12] << 16) ^ (c_bcrypt_base64_alphabet[(r5&0x00000F00)>> 6] << 24);
  w[15] = 0;
  w[16] = 0;
  w[17] = 0;

  u32 E[18] = { 0 };

  expand_key (E, w, pw_len);

  E[ 0] = hc_swap32_S (E[ 0]);
  E[ 1] = hc_swap32_S (E[ 1]);
  E[ 2] = hc_swap32_S (E[ 2]);
  E[ 3] = hc_swap32_S (E[ 3]);
  E[ 4] = hc_swap32_S (E[ 4]);
  E[ 5] = hc_swap32_S (E[ 5]);
  E[ 6] = hc_swap32_S (E[ 6]);
  E[ 7] = hc_swap32_S (E[ 7]);
  E[ 8] = hc_swap32_S (E[ 8]);
  E[ 9] = hc_swap32_S (E[ 9]);
  E[10] = hc_swap32_S (E[10]);
  E[11] = hc_swap32_S (E[11]);
  E[12] = hc_swap32_S (E[12]);
  E[13] = hc_swap32_S (E[13]);
  E[14] = hc_swap32_S (E[14]);
  E[15] = hc_swap32_S (E[15]);
  E[16] = hc_swap32_S (E[16]);
  E[17] = hc_swap32_S (E[17]);

  for (u32 i = 0; i < 18; i++)
  {
    tmps[gid].E[i] = E[i];
  }

  /**
   * salt
   */

  u32 salt_buf[4];

  salt_buf[0] = salt_bufs[SALT_POS_HOST].salt_buf[0];
  salt_buf[1] = salt_bufs[SALT_POS_HOST].salt_buf[1];
  salt_buf[2] = salt_bufs[SALT_POS_HOST].salt_buf[2];
  salt_buf[3] = salt_bufs[SALT_POS_HOST].salt_buf[3];

  #ifdef BCRYPT_AVOID_BANK_CONFLICTS
  S0 = S + (FIXED_LOCAL_SIZE * 256 * 0);
  S1 = S + (FIXED_LOCAL_SIZE * 256 * 1);
  S2 = S + (FIXED_LOCAL_SIZE * 256 * 2);
  S3 = S + (FIXED_LOCAL_SIZE * 256 * 3);
  #else
  S0 = S0_all[lid];
  S1 = S1_all[lid];
  S2 = S2_all[lid];
  S3 = S3_all[lid];
  #endif

  blowfish_set_key_salt (E, 18, salt_buf, P, S0, S1, S2, S3);

  // store

  for (u32 i = 0; i < 18; i++)
  {
    tmps[gid].P[i] = P[i];
  }

  for (u32 i = 0; i < 256; i++)
  {
    tmps[gid].S0[i] = GET_KEY32 (S0, i);
    tmps[gid].S1[i] = GET_KEY32 (S1, i);
    tmps[gid].S2[i] = GET_KEY32 (S2, i);
    tmps[gid].S3[i] = GET_KEY32 (S3, i);
  }
}

KERNEL_FQ KERNEL_FA void m33800_loop2 (KERN_ATTR_TMPS (bcrypt_tmp_t))
{
  /**
   * base
   */

  const u64 gid = get_global_id (0);
  const u64 lid = get_local_id (0);

  if (gid >= GID_CNT) return;

  // load

  u32 E[18];

  for (u32 i = 0; i < 18; i++)
  {
    E[i] = tmps[gid].E[i];
  }

  u32 P[18];

  for (u32 i = 0; i < 18; i++)
  {
    P[i] = tmps[gid].P[i];
  }

  #ifdef DYNAMIC_LOCAL
  // from host
  #else
  LOCAL_VK u32 S0_all[FIXED_LOCAL_SIZE][256];
  LOCAL_VK u32 S1_all[FIXED_LOCAL_SIZE][256];
  LOCAL_VK u32 S2_all[FIXED_LOCAL_SIZE][256];
  LOCAL_VK u32 S3_all[FIXED_LOCAL_SIZE][256];
  #endif

  #ifdef BCRYPT_AVOID_BANK_CONFLICTS
  LOCAL_AS u32 *S0 = S + (FIXED_LOCAL_SIZE * 256 * 0);
  LOCAL_AS u32 *S1 = S + (FIXED_LOCAL_SIZE * 256 * 1);
  LOCAL_AS u32 *S2 = S + (FIXED_LOCAL_SIZE * 256 * 2);
  LOCAL_AS u32 *S3 = S + (FIXED_LOCAL_SIZE * 256 * 3);
  #else
  LOCAL_AS u32 *S0 = S0_all[lid];
  LOCAL_AS u32 *S1 = S1_all[lid];
  LOCAL_AS u32 *S2 = S2_all[lid];
  LOCAL_AS u32 *S3 = S3_all[lid];
  #endif

  for (u32 i = 0; i < 256; i++)
  {
    SET_KEY32 (S0, i, tmps[gid].S0[i]);
    SET_KEY32 (S1, i, tmps[gid].S1[i]);
    SET_KEY32 (S2, i, tmps[gid].S2[i]);
    SET_KEY32 (S3, i, tmps[gid].S3[i]);
  }

  /**
   * salt
   */

  u32 salt_buf[4];

  salt_buf[0] = salt_bufs[SALT_POS_HOST].salt_buf[0];
  salt_buf[1] = salt_bufs[SALT_POS_HOST].salt_buf[1];
  salt_buf[2] = salt_bufs[SALT_POS_HOST].salt_buf[2];
  salt_buf[3] = salt_bufs[SALT_POS_HOST].salt_buf[3];

  /**
   * main loop
   */

  for (u32 i = 0; i < LOOP_CNT; i++)
  {
    for (u32 i = 0; i < 18; i++)
    {
      P[i] ^= E[i];
    }

    blowfish_encrypt (P, S0, S1, S2, S3);

    P[ 0] ^= salt_buf[0];
    P[ 1] ^= salt_buf[1];
    P[ 2] ^= salt_buf[2];
    P[ 3] ^= salt_buf[3];
    P[ 4] ^= salt_buf[0];
    P[ 5] ^= salt_buf[1];
    P[ 6] ^= salt_buf[2];
    P[ 7] ^= salt_buf[3];
    P[ 8] ^= salt_buf[0];
    P[ 9] ^= salt_buf[1];
    P[10] ^= salt_buf[2];
    P[11] ^= salt_buf[3];
    P[12] ^= salt_buf[0];
    P[13] ^= salt_buf[1];
    P[14] ^= salt_buf[2];
    P[15] ^= salt_buf[3];
    P[16] ^= salt_buf[0];
    P[17] ^= salt_buf[1];

    blowfish_encrypt (P, S0, S1, S2, S3);
  }

  // store

  for (u32 i = 0; i < 18; i++)
  {
    tmps[gid].P[i] = P[i];
  }

  for (u32 i = 0; i < 256; i++)
  {
    tmps[gid].S0[i] = GET_KEY32 (S0, i);
    tmps[gid].S1[i] = GET_KEY32 (S1, i);
    tmps[gid].S2[i] = GET_KEY32 (S2, i);
    tmps[gid].S3[i] = GET_KEY32 (S3, i);
  }
}

KERNEL_FQ KERNEL_FA void m33800_comp (KERN_ATTR_TMPS (bcrypt_tmp_t))
{
  /**
   * base
   */

  const u64 gid = get_global_id (0);
  const u64 lid = get_local_id (0);

  if (gid >= GID_CNT) return;

  // load

  u32 P[18];

  for (u32 i = 0; i < 18; i++)
  {
    P[i] = tmps[gid].P[i];
  }

  #ifdef DYNAMIC_LOCAL
  // from host
  #else
  LOCAL_VK u32 S0_all[FIXED_LOCAL_SIZE][256];
  LOCAL_VK u32 S1_all[FIXED_LOCAL_SIZE][256];
  LOCAL_VK u32 S2_all[FIXED_LOCAL_SIZE][256];
  LOCAL_VK u32 S3_all[FIXED_LOCAL_SIZE][256];
  #endif

  #ifdef BCRYPT_AVOID_BANK_CONFLICTS
  LOCAL_AS u32 *S0 = S + (FIXED_LOCAL_SIZE * 256 * 0);
  LOCAL_AS u32 *S1 = S + (FIXED_LOCAL_SIZE * 256 * 1);
  LOCAL_AS u32 *S2 = S + (FIXED_LOCAL_SIZE * 256 * 2);
  LOCAL_AS u32 *S3 = S + (FIXED_LOCAL_SIZE * 256 * 3);
  #else
  LOCAL_AS u32 *S0 = S0_all[lid];
  LOCAL_AS u32 *S1 = S1_all[lid];
  LOCAL_AS u32 *S2 = S2_all[lid];
  LOCAL_AS u32 *S3 = S3_all[lid];
  #endif

  for (u32 i = 0; i < 256; i++)
  {
    SET_KEY32 (S0, i, tmps[gid].S0[i]);
    SET_KEY32 (S1, i, tmps[gid].S1[i]);
    SET_KEY32 (S2, i, tmps[gid].S2[i]);
    SET_KEY32 (S3, i, tmps[gid].S3[i]);
  }

  /**
   * main
   */

  u32 L0;
  u32 R0;

  L0 = BCRYPTM_0;
  R0 = BCRYPTM_1;

  for (u32 i = 0; i < 64; i++)
  {
    BF_ENCRYPT (L0, R0);
  }

  const u32 r0 = L0;
  const u32 r1 = R0;

  L0 = BCRYPTM_2;
  R0 = BCRYPTM_3;

  for (u32 i = 0; i < 64; i++)
  {
    BF_ENCRYPT (L0, R0);
  }

  const u32 r2 = L0;
  const u32 r3 = R0;

  /*
  e = L0;
  f = R0;

  f &= ~0xff; // its just 23 not 24 !
  */

  #define il_pos 0

  #ifdef KERNEL_STATIC
  #include COMPARE_M
  #endif
}
