import * as gutils from "../../utils";
import * as dt from "date-fns";
import { AvailabilityNotCreatedError } from "./interviewerrors";

/**
 * Most date strings are formated as YYYY-MM-DD. When passed into a Date()
 * object constructor, the constructor will consider it to be a UTC
 * time stamp. This function effectively is a Date constructor for
 * YYYY-MM-DD format strings, but considers those strings to timestamps in the
 * local timezone.
 */
let dateStrAsLocal = (date) => {
  if (date instanceof Date) {
    return date;
  }
  // we will assume date is a string of format YYYY-MM-DD
  const [y, m, d] = date.split("-");
  // Date takes months from 0-11, so subtract 1 from month
  return new Date(y, m - 1, d);
};

export let getCurrentInductionClass = async () => {
  let induction_class_head = await fetch("/api/inductionclasses/");
  if (induction_class_head.status == 404) {
    return null;
  }
  let induction_classes = await induction_class_head.json();
  for (let induction_class of induction_classes) {
    //let currentDate = new Date();
    // TODO: Change currentDate to actually be the current date.
    let currentDate = new Date(2023, 10, 15);
    if (
      dateStrAsLocal(induction_class.start_date) < currentDate &&
      currentDate < dateStrAsLocal(induction_class.end_date)
    ) {
      return induction_class;
    }
  }
  return null;
};

export let getInterviewCycle = async (iCyclePk) =>
  await (await fetch(`/api/interviewcycles/${iCyclePk}`)).json();

export let getAvailability = async (userPk, interviewCyclePk) => {
  let availabilityResponse = await fetch(
    `/api/interviewavailabilities?interview_cycle=${interviewCyclePk}&user_id=${userPk}`,
  );
  let availabilities = await availabilityResponse.json();
  if (availabilities.length == 0) {
    return null;
  }
  return availabilities[0];
};

let timeStrToDate = (time) => {
  const [h, m, s] = time.split(":");
  let asDate = new Date();
  asDate.setHours(h, m, s);
  return asDate;
};

export let slotsInTimeRange = (endTime, startTime) =>
  4 * dt.differenceInHours(timeStrToDate(endTime), timeStrToDate(startTime));

let numInterviewDays = (interviewCycle) =>
  interviewCycle.open_weekends
    ? dt.differenceInCalendarDays(
        interviewCycle.end_date,
        interviewCycle.start_date,
      )
    : dt.differenceInBusinessDays(
        interviewCycle.end_date,
        interviewCycle.start_date,
      );

export let numInterviewCycleSlots = (interviewCycle) =>
  numInterviewDays(interviewCycle) *
  slotsInTimeRange(interviewCycle.end_time, interviewCycle.start_time);

export let interviewCycleToGridWidths = (interviewCycle) => {
  const weeks = dt.eachWeekOfInterval({
    start: dateStrAsLocal(interviewCycle.start_date),
    end: dateStrAsLocal(interviewCycle.end_date),
  });

  if (weeks.length == 1) {
    return [numInterviewDays(interviewCycle)];
  }

  let newIDaysIn = (startDate, endDate) => {
    return {
      open_weekends: interviewCycle.open_weekends,
      start_date: startDate,
      end_date: endDate,
    };
  };

  let gridWidths = [];
  gridWidths.push(
    numInterviewDays(
      newIDaysIn(dateStrAsLocal(interviewCycle.start_date), weeks[1]),
    ),
  );
  for (let i = 1; i < weeks.length - 1; ++i) {
    gridWidths.push(numInterviewDays(newIDaysIn(weeks[i], weeks[i + 1])));
  }
  gridWidths.push(
    numInterviewDays(
      newIDaysIn(
        weeks[weeks.length - 1],
        dateStrAsLocal(interviewCycle.end_date),
      ),
    ),
  );
  return gridWidths;
};

function* repeatGen(len, val) {
  for (let i = 0; i < len; ++i) {
    yield val;
  }
}
export let newAvailability = (interviewCycle) => new Uint8Array(numInterviewCycleSlots(interviewCycle));

export let postAvailability = async (userPk, slots, interviewCyclePk) => {
  let availability = {
    user: userPk,
    slots: bytesToBase64(slots),
    interview_cycle: interviewCyclePk,
  };

  let request = gutils.csrfSafeReq("POST", JSON.stringify(availability));
  let response = await fetch("/api/interviewavailabilities", request);
  if (response.status != 200 && response.status != 201) {
    throw new AvailabilityNotCreatedError(
      "Availability could not be posted for some reason, for interview Cycle ${interviewCyclePk}",
      interviewCyclePk,
    );
  }
  return response;
};

export let putAvailability = async (putId, slotsBinary) => {
  let availabilityDif = {
    slots: bytesToBase64(slotsBinary),
  };
  let response = await fetch(
    `/api/interviewavailabilities/${putId}`,
    gutils.csrfSafeReq("PATCH", JSON.stringify(availabilityDif)),
  );
  return response;
};

// from https://developer.mozilla.org/en-US/docs/Glossary/Base64
export let base64ToBytes = (base64) =>
  Uint8Array.from(atob(base64), (m) => m.codePointAt(0));

// from https://developer.mozilla.org/en-US/docs/Glossary/Base64
export let bytesToBase64 = (bytes) => {
  const binString = Array.from(bytes, (byte) =>
    String.fromCodePoint(byte),
  ).join("");
  return btoa(binString);
};

function* gridsToBoolStream(grids) {
  for (let grid of grids) {
    let gridHeight = grid.length;
    let gridWidth = grid[0].length;
    for (let x = 0; x < gridWidth; ++x) {
      for (let y = 0; y < gridHeight; ++y) {
        yield grid[y][x];
      }
    }
  }
}

export let availabilityGridsToBinary = (grids) => {
  let numBits = grids.reduce((accumulator, grid) => (accumulator + grid.length * grid[0].length), 0);
  let numBytes =
    numBits % 8 == 0 ? Math.trunc(numBits / 8) : Math.trunc(numBits / 8) + 1;
  let numWastedBits = (8 - (numBits % 8)) % 8;
  let byteArr = new Uint8Array(numBytes);

  let curBit = 0;
  for (let gridVal of gridsToBoolStream(grids)) {
    let curByte = Math.trunc(curBit / 8);
    byteArr[curByte] = (byteArr[curByte] << 1) | gridVal;
    ++curBit;
  }

  byteArr[numBytes - 1] = byteArr[numBytes - 1] << numWastedBits;

  return byteArr;
};

export let slotsBinaryValidForInterviewCycle = (slotsBinary, interviewCycle) =>
  slotsBinary.length * 8 >= numInterviewCycleSlots(interviewCycle);

export let prefixSum = (arr) => {
    let result = [0];
    for (let i = 0; i < arr.length; ++i) {
        result.push(arr[i] + result[i]);
    }
    return result;
}
